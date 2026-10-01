# 公式設備図と会場モデルの比較

対象：TRC Eホール設備図 2025/12版。比較日：2026-10-01。

[3ページの日本語比較レポート](JRRF_official_PDF_comparison.pdf)と、検証数値のJSON・CSVを収録しています。原図の図形は比較のための限定的な引用であり、出典は公式設備図です。

図形を1/250で測った場合の約10%の過大読みと、同じ図面の10mスケールバーの整合を確認しました。図面の記載寸法まで一律に約10%誤っているという意味ではありません。

レポート・`JRRF_PDF_column_comparison_mm.csv` の柱中心差最大122.3mmは、補正した元PDF図形の外接矩形中心とスキャン版の中心を合わせた比較です。図形と寸法線の不整合も含みます。

後から寸法列を優先して作り直したPDF版の柱中心差は `model_comparison_centres.json` に分けています。9本の平均中心を一致させる平行移動のみで位置合わせし、最大約62.0mmです。どちらも現地に対する精度証明ではありません。

会場面積、南西の暫定床境界、反射するガラス、扉の有効開口などの制約はレポートと各モデルの説明を参照してください。

モデル再構築・分析：Map model by https://github.com/Psych0h3ad

出典：3DMart Japan / Japan RepRap Festival / Realsee（https://realsee.ai/VbOOJVjA）、株式会社東京流通センター（https://www.trc-event.jp/download/pdf/setsubi_e.pdf）。
