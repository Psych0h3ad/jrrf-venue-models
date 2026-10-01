# 検証スクリプト

リポジトリを展開した状態で実行します。検証JSONを各モデルのフォルダに書き込みます。

```sh
blender --background --python tools/verify_native.py
python tools/verify_exports.py
```

確認環境：Blender 5.2.2 LTS。交換形式の確認にはPython、numpy、trimeshが必要です。
元スキャン・公式PDFの取得は行いません。形状の閉じ方、モデル内の寸法、交換形式への保持を確認するもので、現地の精度を証明するものではありません。
