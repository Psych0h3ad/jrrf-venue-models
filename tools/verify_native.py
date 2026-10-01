"""Run with Blender: blender --background --python tools/verify_native.py

Verify native geometry and printed/derived dimensions, not physical survey accuracy.
"""
from pathlib import Path
import json, bpy, bmesh

ROOT=Path(__file__).resolve().parents[1]
GROUPS={
 'scan':['01_Floor','02_Walls','03_Columns','04_Glazing_and_entrance_zones','09_Observed_upper_projections'],
 'pdf':['01_PDF_Floors','02_PDF_Walls','03_PDF_Dimensioned_columns','04_PDF_Dimensioned_entrances','05_PDF_Lowered_ceiling_2540','06_PDF_Keep_clear_floor_zones'],
}

for kind,stem,expected_count in [('scan','JRRF_venue_layout',41),('pdf','JRRF_PDF_venue',88)]:
    folder=ROOT/'models'/kind; filename=stem+'.blend'
    j=json.loads((folder/(stem+'.json')).read_text(encoding='utf-8'))
    bpy.ops.wm.open_mainfile(filepath=str(folder/filename))
    bpy.context.view_layer.update()
    parts=[]
    for cn in GROUPS[kind]:
        for ob in bpy.data.collections[cn].objects:
            if ob.type!='MESH':continue
            bm=bmesh.new();bm.from_mesh(ob.data)
            parts.append({'id':ob.name,'closed':all(len(e.link_faces)==2 for e in bm.edges),
                          'volume_m3':bm.calc_volume(signed=True)})
            bm.free()
    columns=[]
    for a in j['columns']:
        ob=bpy.data.objects[a['id']]
        expected=[a['xmax']-a['xmin'],a['ymax']-a['ymin'],j['height_m']] if kind=='scan' else [a['width_m'],a['depth_m'],j['height_m']]
        error=max(abs(v-w) for v,w in zip(ob.dimensions,expected))
        columns.append({'id':a['id'],'dimensions_m':list(ob.dimensions),'max_size_error_m':error})
    checks={
        'model_part_count':len(parts)==expected_count,
        'all_model_parts_closed':all(p['closed'] for p in parts),
        'all_model_parts_positive_volume':all(p['volume_m3']>0 for p in parts),
        'nine_column_dimensions_match_metadata':len(columns)==9 and all(c['max_size_error_m']<4e-6 for c in columns),
        'metric_scale_1':bpy.context.scene.unit_settings.system=='METRIC' and bpy.context.scene.unit_settings.scale_length==1,
        'no_raw_scan_reference':bpy.data.objects.get('Public_scan_reference_630957_triangles') is None,
        'no_original_pdf_image':not bpy.data.images and bpy.data.objects.get('Original_PDF_plan_reference') is None,
        'no_external_libraries':not bpy.data.libraries,
        'required_credit_embedded':bpy.context.scene.get('required_credit')=='Map model by https://github.com/Psych0h3ad',
    }
    result={'file':filename,'passed':False,'checks':checks,'mesh_parts':parts,'column_measurements':columns,
            'interpretation':'Topology and model-dimension checks; no as-built accuracy certification.'}
    if kind=='pdf':
        west=bpy.data.objects['PDF_West_reference'].location
        width=(bpy.data.objects['PDF_East_reference'].location-west).length
        depth=(bpy.data.objects['PDF_North_reference'].location-west).length
        checks['reference_47520_by_40380_mm']=abs(width-47.52)<2e-6 and abs(depth-40.38)<2e-6
        low=bpy.data.objects['SW_lowered_ceiling']
        zmin=min((low.matrix_world@v.co).z for v in low.data.vertices)
        checks['lowered_ceiling_6540_4530_2540_mm']=abs(low.dimensions.x-6.54)<2e-6 and abs(low.dimensions.y-4.53)<2e-6 and abs(zmin-2.54)<2e-6
        doors=[]
        for a in j['doors']:
            if a['kind']!='double_leaf_entrance':continue
            lo=bpy.data.objects[a['id']+'_jamb_lo'];hi=bpy.data.objects[a['id']+'_jamb_hi']
            w=min((hi.matrix_world@v.co).y for v in hi.data.vertices)-max((lo.matrix_world@v.co).y for v in lo.data.vertices)
            h=max((lo.matrix_world@v.co).z for v in lo.data.vertices)
            doors.append({'id':a['id'],'width_m':w,'height_m':h})
        checks['eight_1780_by_2100_openings']=len(doors)==8 and all(abs(a['width_m']-1.78)<2e-6 and abs(a['height_m']-2.1)<2e-6 for a in doors)
        checks['reconstructed_scan_reference_hidden']=bpy.data.collections['10_Scan_model_reference_hidden'].hide_viewport
        result.update(reference_width_m=width,reference_depth_m=depth,entrance_measurements=doors,lowered_ceiling_underside_m=zmin)
    result['passed']=all(checks.values())
    (folder/'public_native_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'model':kind,'passed':result['passed'],'parts':len(parts),'checks':checks}))
    assert result['passed'], 'Native model validation failed'
