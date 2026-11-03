# 色処理の試作 v0.2

## 今回追加する二つの処理

1. **提供APKの暖色・寒色計算の移植。** 元の `CameraController.getAwbColorCompensationRggbVector()` をそのまま呼び出し、赤のゲインに `調整値 × 0.05` を足し、青から同じ量を引きます。既存スライダーの範囲は元の `StateMachine.updateAmberBlueColor()` にある−7〜＋7です。以前のSony専用要求キーに代えて、標準Camera2のホワイトバランス・色補正ゲイン・変換行列へ渡します。
2. **Web比較チャートから求めた保存写真用の補正。** 上部の「色」ボタンでオン／オフと強さ0〜100%を指定できます。新規インストール時はオフ、強さの初期値は35%。JPEG保存時だけに作用し、この補正自体はプレビューと動画には作用しません。JPEGは再圧縮されます。

暖色・寒色の基準には自動ホワイトバランス時の値だけを使い、手動補正された結果を再び基準に取り込まないようにします。0／リセットでは自動へ戻ります。機種・レンズの制約で標準色補正を使えない場合は自動を維持します。これはSonyの画像処理エンジン全体の移植ではありません。

## Web比較に使った資料

- [Notebookcheck: Galaxy S26レビュー](https://www.notebookcheck.net/Exynos-and-more-battery-power-make-it-a-star-Samsung-Galaxy-S26-review.1284566.0.html) 内の撮影用ColorChecker明所画像。[画像](https://www.notebookcheck.net/fileadmin/_processed_/8/6/csm_Photo_GalaxyS26_ColorChecker_60f42351ef.jpg)
- [Notebookcheck: Xperia 1 VIIレビュー](https://www.notebookcheck.pl/Recenzja-Sony-Xperia-1-VII-wymarzony-smartfon-dla-tworcow-tresci-i-entuzjastow-fotografii.1122762.0.html) 内の撮影用ColorChecker明所画像。[画像](https://www.notebookcheck.net/fileadmin/_processed_/5/8/csm_Photo_Xperia1_ColorChecker_3570738a6b.jpg)

ディスプレーの色測定画像や、1ルクスの暗所画像は計算に使っていません。24個の色票から中心24×24画素の中央値を採り、sRGBを線形RGBへ変換して3×3行列を求めました。黒が浮かないよう、オフセットは加えません。極端な変換を抑える正則化を使い、色票を一つずつ除外した検証で正則化量を選んでいます。

明所チャート間のRGB誤差（8bit値のRMSE）は、補正前18.41、色票を一つずつ除外した検証で11.59、全色票を使った当てはめでは10.86でした。これはこの2枚のチャート上の数値です。**別の風景・人物・照明や、SC-51Gで同様に改善することを示す数値ではありません。** ΔEの値でもありません。

掲載GalaxyはExynos版で、対象SC-51Gとはハードウェアが違います。また、撮影日時・ファームウェア・純正アプリの画像処理と、移植アプリの出力にも差があります。元のAPKが搭載されていたXperiaと、比較に使ったXperia 1 VIIも同一機種だとは確認していません。従って「Sony純正色を再現」「SC-51Gを校正済み」とは呼べません。

## 実装と検証

- 画像は端末内で処理します。撮影写真をWebへ送る機能は追加していません。
- 補正オフ／強さ0では元のJPEGをそのまま保存経路へ渡します。
- 補正オンではsRGBへ展開し、色行列を指定強度で混ぜ、JPEG品質97で再圧縮します。
- 元JPEGのEXIFセグメントを保持します。元の圧縮データ位置やHDRゲインマップは再圧縮後に使えないためコピーしません。
- メモリー不足や処理エラーの際は、元JPEGを保存経路へ戻します。
- 10万画素の強さ0での完全一致・アルファ保持、黒の保持、ゲイン範囲、EXIF引き継ぎのホスト検証が通っています。
- 最初の実機検証では、標準と補正35%の4000×3000 JPEGを保存できました。補正追加時間は約215msでした。
- 修正後の最終確認でも4000×3000 JPEGを保存し、補正追加時間は約291msでした。取得した標準／補正JPEGはいずれも正常に読み取れ、EXIFの向き（6）が保持されていました。
- 暖色・寒色の実機結果：自動時R=1.8555/B=1.8184、＋7でR=2.2051/B=1.4688、−7でR=1.5059/B=2.1680、再度＋7でR=2.2061/B=1.4697。元の式どおり約±0.35の変化で、繰り返しによる蓄積が止まることを確認しました。リセット後は自動モードへ復帰しました。
- 主に背面広角・明所での検証です。暖色調整を保ったままのレンズ切り替え、混合光、暗所、全撮影モードの色精度は未検証です。

数値資料は `analysis/color-reference/fit-report.json`、再計算は `tools/fit-color-reference.py`。アプリに組み込む数値は `src/local/sc51g/ColorReference.java` に生成されます。写真の色味の良し悪しは、複数の場面で見比べながら調整する必要があります。
