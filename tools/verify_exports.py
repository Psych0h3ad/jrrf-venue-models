"""Run with Python and numpy/trimesh: python tools/verify_exports.py.

Verify exchange geometry, not physical survey accuracy.
"""
from pathlib import Path
import json, numpy as np, trimesh

ROOT=Path(__file__).resolve().parents[1]
for kind,stem,count in [('scan','JRRF_venue_layout',41),('pdf','JRRF_PDF_venue',88)]:
    folder=ROOT/'models'/kind
    j=json.loads((folder/(stem+'.json')).read_text(encoding='utf-8'))
    scene=trimesh.load(folder/(stem+'.glb'),force='scene',merge_primitives=True)
    scene.apply_transform(np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]]))
    geometry={}
    for node in scene.graph.nodes_geometry:
        transform,name=scene.graph[node];mesh=scene.geometry[name].copy();mesh.apply_transform(transform)
        geometry[name]=mesh
    parts=[]
    for name,m in geometry.items():
        m.merge_vertices()
        parts.append({'id':name,'closed':bool(m.is_watertight),'volume_m3':float(m.volume)})
    cols=[]
    for a in j['columns']:
        size=geometry[a['id']].extents
        expected=np.array([a['xmax']-a['xmin'],a['ymax']-a['ymin'],j['height_m']] if kind=='scan' else [a['width_m'],a['depth_m'],j['height_m']])
        cols.append({'id':a['id'],'dimensions_m':size.tolist(),'max_size_error_m':float(abs(size-expected).max())})
    obj=trimesh.load(folder/(stem+'.obj'),force='scene')
    checks={'part_count':len(parts)==count,'all_parts_closed':all(p['closed'] for p in parts),
            'all_parts_positive_volume':all(p['volume_m3']>0 for p in parts),
            'nine_columns_preserved':len(cols)==9 and all(c['max_size_error_m']<4e-6 for c in cols),
            'glb_obj_bounds_agree':bool(abs(scene.bounds-obj.bounds).max()<4e-6)}
    if kind=='pdf':
        checks['lowered_ceiling_underside_2540_mm']=bool(abs(geometry['SW_lowered_ceiling'].bounds[0,2]-2.54)<4e-6)
        checks['printed_dimension_chains_preserved']=bool(abs(sum(j['horizontal_dimension_chain_m'])-47.52)<1e-9 and abs(sum(j['vertical_dimension_chain_m'])-40.38)<1e-9)
    result={'passed':all(checks.values()),'checks':checks,'parts':parts,'column_measurements':cols,
            'bounds_m':scene.bounds.tolist(),'triangles':sum(len(m.faces) for m in geometry.values()),
            'interpretation':'Geometry and metadata preservation; no as-built accuracy certification.'}
    (folder/'public_export_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'model':kind,'passed':result['passed'],'parts':len(parts),'checks':checks}))
    assert result['passed'], 'Export validation failed'
