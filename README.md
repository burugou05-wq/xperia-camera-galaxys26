# Xperiaカメラ SC-51G / One UI 9 移植試作版

**Xperiaの撮影UIをGalaxy S26へ。音量キーでズーム、色とシャッター音も調整。**

[![Download APK](https://img.shields.io/badge/Download-APK-3DDC84?logo=android&logoColor=white)](https://github.com/burugou05-wq/xperia-camera-sc51g/releases/tag/v0.2)
![Device](https://img.shields.io/badge/Galaxy_S26-SC--51G-1428A0)
![Status](https://img.shields.io/badge/Status-Experimental-orange)

Xperiaカメラの操作感をGalaxy S26で試す、非公式の移植プロジェクト。背面0.6×・1×・3×、音量ボタンによるズーム、シャッター音調整に対応し、暖色・寒色の調整と実験的な写真用色補正を追加しました。

**An experimental Xperia camera port for Samsung Galaxy S26 (SC-51G), Android 17 / One UI 9.** Features volume-key zoom, rear 0.6× / 1× / 3× presets, adjustable shutter sound, warm/cool controls and optional JPEG color correction. Tested on SC-51G only; this is an unofficial prototype, not a reproduction of Sony's imaging engine.

→ **[APKをダウンロード / Download](https://github.com/burugou05-wq/xperia-camera-sc51g/releases/tag/v0.2)** · [色処理の仕組み](COLOR-PROCESSING.md)

## v0.2：色処理を追加

最新のAPKは [Releases](https://github.com/burugou05-wq/xperia-camera-sc51g/releases) の **Assets** にある `xperia-camera-sc51g-oneui9-v0.2.apk` です。非公式の試作版です。提供APKに残っていた暖色・寒色の計算を標準Camera2へ接続し、上部の「色」ボタンにWeb比較チャートから求めた写真用補正を追加しました。Web比較補正は初期状態ではオフです。

詳細・元資料・実機結果・制約は [色処理の説明](COLOR-PROCESSING.md) を参照してください。Sony純正の画像処理エンジン全体の移植ではありません。v0.2はプレリリースとして公開しています。

対象はユーザー所有のGalaxy S26 SC-51G、Android 17（API 37）/ One UI 9。入力APKは `camera-2-9-a-0-24.apk`（パッケージ `com.sonyericsson.android.camera`、表示バージョン2.9.A.0.24）。入力ファイルは変更していません。提供APKには固定カメラIDやズーム処理など既存の改変が見られ、Sony公式の未改変バイナリであることは確認していません。

## 使い方

- 画面の倍率ボタン：0.6倍、1倍、3倍。ズームは背面の公開範囲0.6〜10倍に制限します。
- 音量＋：ズームイン。音量−：ズームアウト。元APKにあるズーム操作を維持しています。
- 上部ショートカット列のスピーカーボタン：シャッター音のオン／消音、1〜100%の音量、試聴。設定は保存されます。再生音量は端末のメディア音量にも連動します。
- 新ボタンは既存のフラッシュ・タイマーと同じ列に配置し、画面余白で隠れる元の配置も調整しました。
- 写真・動画の保存先：DCIM/Camera。

## 実機で確認したこと

2026-11-03、接続済みの対象端末で確認。

| 項目 | 結果 |
| --- | --- |
| 起動・プレビュー | 動作 |
| 背面超広角 | 実センサーID 2、焦点距離2.2mmを取得 |
| 背面広角 | 実センサーID 5、焦点距離5.4mmを取得 |
| 背面望遠 | 約3倍で実センサーID 6、焦点距離7.0mmを取得 |
| 前面への切り替え | 焦点距離3.3mmの映像を取得 |
| 音量キー | 1.0165倍→＋で1.1408倍→−で1.0165倍に復帰 |
| 写真 | 4000×3000 JPEGの保存を確認 |
| 消音での写真 | 消音設定で新しいJPEGの保存を確認 |
| 動画 | 1920×1080、約5.5秒のMP4保存を確認 |
| シャッター音 | 指定ゲインでのSoundPool再生、消音切り替え、設定保持を確認 |
| 設定画面 | 空の選択肢の項目を隠した版で、表示と撮影画面への復帰を確認 |
| APK | 再構築・16KB ZIPページ配置・署名検証・実機インストールを確認 |

倍率に応じたレンズ選択はSamsungのカメラドライバーが行います。暗さや被写体までの距離などにより、3倍表示でも広角の切り出しを選ぶことがあります。3倍を常に望遠へ固定する実装ではありません。

## 変更の要点

- Sonyの必須共有ライブラリ指定を任意に変更。
- Sony向け固定ID 3/4などを使わず、SC-51Gの背面論理カメラ0・前面1を使用。
- 背面論理カメラ配下の超広角・広角・望遠を標準 `CONTROL_ZOOM_RATIO` で制御。
- 最大ズーム、露出時間の範囲、複数物理カメラの有無を標準Camera2情報から取得。
- Sony専用セッション設定・要求キーをGalaxyへ送らないように変更。未知の要求キーを読み取る際のクラッシュも回避。
- Sony専用の仮想JPEG後処理カメラは開かず、標準JPEG保存を使用。
- AF設定の反映確認に標準のAFモード・AEモード・AF領域を使用。
- 設定画面では、フィルター後の選択肢が空の項目を隠すよう修正。
- 追加の音量設定はアプリ内だけに保存し、端末全体の音量設定は変更しません。音源は提供APK内のシャッター音を使用します。動画の開始・停止音は元の経路です。

## 対応範囲と残る制約

これはGalaxy上で動かすための試作移植です。Sonyと同一の画像処理や画質を再現したものではありません。操作画面は提供APKを土台にしていますが、センサー処理と画像生成はSamsungの公開カメラ経路を使います。

- 50MP撮影、RAW保存、Samsung純正アプリ専用の高度な処理は追加していません。確認済みの静止画は12MPです。
- Sony専用HDR、シーン認識、背景処理、特殊撮影を同等に移植したものではありません。
- ISOとシャッター速度を両方指定する標準Camera2経路は残っていますが、全マニュアル設定の画作り・精度は未検証です。元APKのQualcomm固有タグに依存するISO優先／シャッター優先の自動制御は動作を保証しません。
- 4K、高フレームレート、スローモーション、長時間録画、全撮影条件は未検証です。
- 端末内のテスト用写真・短い動画は自動削除していません。

## 再構築

JDK 17、Python 3、Android SDK（platforms/android-35、build-tools/36.0.0）、[Apktool 3.0.3](https://github.com/iBotPeaches/Apktool/releases/tag/v3.0.3) が必要です。ApktoolのJARを `tools/apktool.jar` に置きます。SDKは `ANDROID_SDK_ROOT` / `ANDROID_HOME` またはWindowsの既定配置から参照します。

元APKはリポジトリに含めていません。手元で適切に入手した、対象と同一の `camera-2-9-a-0-24.apk` をルートに置いてください。別バージョンへのパッチ適用は未対応です。

対象入力APKのSHA-256：`04a7b4c30259ab0cc1466addf38a6be5dff904b74f8c40cf4e60551a50386d7c`。

```powershell
.\setup-port.ps1
.\build-port.ps1
```

`src/` は追加ボタン・音処理・色処理、`patches/` はCamera2互換処理、`tools/patch_port.py` は展開コードへの変更です。出力は `out/xperia-camera-sc51g-test.apk`。ローカル署名鍵は初回ビルド時に `keys/port-test.jks` に生成されます。公開APKとは鍵が異なるため、そのまま上書き更新はできません。

色計算の再実行にはNumPyとPillow、および [色処理の説明](COLOR-PROCESSING.md) に記載の参照画像を `analysis/color-reference/galaxy-chart.jpg` と `xperia-chart.jpg` に用意してください。参照画像そのものは含めていません。

## 公開物について

Sony / Samsungの公式プロジェクトではありません。提供APKを土台にした互換性の試作であり、Sony純正ISPの移植や全機能の動作を保証するものではありません。Sony由来のアプリ本体・名称・画像・音源などの権利は元の権利者に帰属します。本リポジトリはそれらに新しい利用許諾を与えるものではありません。

秘密鍵、端末の接続情報、実機ログ、テスト写真・動画、展開済みの元コードは含めていません。APKはリリースのAssetsで配布します。網羅的なデバッグは行っていません。

参考：[Android公式 Multi-camera API](https://developer.android.com/media/camera/camera2/multi-camera)、[ドコモ SC-51G仕様](https://www.docomo.ne.jp/product/sc51g/spec.html)。
