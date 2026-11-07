# Xperia Camera for Galaxy S26 — SC-51G / One UI 9

<a id="languages"></a>

**[日本語](#japanese) · [English](#english)**

<a id="japanese"></a>

## 日本語

**Xperiaの撮影UIをGalaxy S26へ。音量キーでズーム、色とシャッター音も調整。**

![Distribution](https://img.shields.io/badge/Distribution-Source_only-blue)
![Device](https://img.shields.io/badge/Galaxy_S26-SC--51G-1428A0)
![Status](https://img.shields.io/badge/Status-Experimental-orange)

Xperiaカメラの操作感をGalaxy S26で試す、非公式の移植プロジェクト。背面0.6×・1×・3×、音量ボタンによるズーム、シャッター音調整に対応し、暖色・寒色の調整と実験的な写真用色補正を追加しました。

**An experimental Xperia camera port for Samsung Galaxy S26 (SC-51G), Android 17 / One UI 9.** Features volume-key zoom, rear 0.6× / 1× / 3× presets, adjustable shutter sound, warm/cool controls and optional JPEG color correction. Tested on SC-51G only; this is an unofficial prototype, not a reproduction of Sony's imaging engine.

→ **APKは配布していません。** [手元でビルドする](#再構築) · [配布方針](#配布方針) · [色処理の仕組み](COLOR-PROCESSING.md)

## v0.2：色処理を追加

v0.2では、提供APKに残っていた暖色・寒色の計算を標準Camera2へ接続し、上部の「色」ボタンにWeb比較チャートから求めた写真用補正を追加しました。Web比較補正は初期状態ではオフです。**ビルド済みAPKの配布は行っていません。** ソース、パッチ、ビルドスクリプトを公開し、各自の手元でビルドする形にしています（[配布方針](#配布方針)）。

詳細・元資料・実機結果・制約は [色処理の説明](COLOR-PROCESSING.md) を参照してください。Sony純正の画像処理エンジン全体の移植ではありません。以下の実機結果は、2026-11-03にビルドしたv0.2で取得したものです。

対象はユーザー所有のGalaxy S26 SC-51G、Android 17（API 37）/ One UI 9。入力APKは `camera-2-9-a-0-24.apk`（パッケージ `com.sonyericsson.android.camera`、表示バージョン2.9.A.0.24）。入力ファイルは変更していません。提供APKには固定カメラIDやズーム処理など既存の改変が見られ、Sony公式の未改変バイナリであることは確認していません。

## ビルドしてインストール

配布APKはありません。手元でビルドしたAPKを端末に入れます。ビルド手順の詳細は [再構築](#再構築) にあります。

1. 対象と同一の `camera-2-9-a-0-24.apk` を用意し、リポジトリのルートに置きます。
2. Windows では `setup-port.ps1` → `build-port.ps1`、Linux / macOS では `setup-port.sh` → `build-port.sh` を実行します。
3. `out/xperia-camera-sc51g-test.apk` を端末へ転送し、インストールします。
4. アプリを起動し、撮影に必要なカメラ・マイクなどの権限を許可します。

同じパッケージ名 `com.sonyericsson.android.camera` の別署名アプリがあるとインストールできない場合があります。ローカルビルドは初回に `keys/port-test.jks` を生成し、その鍵で署名します。過去に配布したv0.2のAPKとは署名鍵が異なるため、その上への上書き更新はできません。

参考：2026-11-03に配布したv0.2のAPKのSHA-256は `155c4b3474ac8034cb5fe94a766b3ec0bf253702d4d192d3bce15de665628b0f` です。すでにダウンロード済みのコピーを照合するためだけの記録で、現在は配布していません。

## 使い方

- 画面の倍率ボタン：0.6倍、1倍、3倍。ズームは背面の公開範囲0.6〜10倍に制限します。
- 音量＋：ズームイン。音量−：ズームアウト。元APKにあるズーム操作を維持しています。
- 上部ショートカット列のスピーカーボタン：シャッター音のオン／消音、1〜100%の音量、試聴。設定は保存されます。再生音量は端末のメディア音量にも連動します。
- 新ボタンは既存のフラッシュ・タイマーと同じ列に配置し、画面余白で隠れる元の配置も調整しました。
- 「色」ボタン：Web比較補正のオン／オフと強さ0〜100%。初期状態はオフ、初期強度は35%。保存JPEGだけに作用し、プレビューと動画には作用しません。オンではJPEGを再圧縮します。
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
- Web比較補正は異なる機種の公開チャートを使った実験で、SC-51Gの校正やSonyの色再現ではありません。参照Galaxyは対象SC-51Gと異なるExynos版で、一般の風景でも改善することを示す比較ではありません。
- 補正35%で4000×3000 JPEGを保存し、追加処理時間は約215〜291msでした。画像の読み取りとEXIFの向きの保持を確認しました。暖色・寒色調整は、繰り返しで補正が蓄積しないことと、自動ホワイトバランスへの復帰も確認しました。
- 端末内のテスト用写真・短い動画は自動削除していません。

## 配布方針

このリポジトリは**APKを配布しません**。公開するのは、パッチ、追加コード、ビルドスクリプト、検証記録です。

改変・再署名したAPKを不特定多数へ配布すると、Sony由来のアプリ本体・音源・画像などについて、権利者が与えた許諾の範囲を超えるおそれがあります。そのため2026-11-07に、v0.2として公開していたAPKの配布を取り下げました。ビルド済みAPKのミラー公開や再配布も、同じ理由で行いません。

- 各自が所有する端末と、適切に入手した対象APKを使い、自分の環境でビルドしてください（[再構築](#再構築)）。
- ビルドしたAPKは自分の端末で使う範囲にとどめ、再配布はしないでください。
- リポジトリに含まれるのは、互換性のための差分と試作コードだけです。Sony / Samsungの公式プロジェクトではありません。

## 再構築

JDK 17、Python 3、Android SDK（platforms/android-35、build-tools/36.0.0）、[Apktool 3.0.3](https://github.com/iBotPeaches/Apktool/releases/tag/v3.0.3) が必要です。ApktoolのJARを `tools/apktool.jar` に置きます。SDKは `ANDROID_SDK_ROOT` / `ANDROID_HOME`、または各OSの既定配置（Windows: `%LOCALAPPDATA%\Android\Sdk`、macOS: `~/Library/Android/sdk`、Linux: `~/Android/Sdk`）から参照します。

元APKはリポジトリに含めていません。手元で適切に入手した、対象と同一の `camera-2-9-a-0-24.apk` をルートに置いてください。別バージョンへのパッチ適用は未対応です。

対象入力APKのSHA-256：`04a7b4c30259ab0cc1466addf38a6be5dff904b74f8c40cf4e60551a50386d7c`。

```powershell
.\setup-port.ps1
.\build-port.ps1
```

```bash
./setup-port.sh
./build-port.sh
```

WindowsのPowerShell版で実機向けビルドを確認しています。Linux / macOS版は同じ処理を移植したもので、このリポジトリの検証環境では実行していません。

`src/` は追加ボタン・音処理・色処理、`patches/` はCamera2互換処理、`tools/patch_port.py` は展開コードへの変更です。出力は `out/xperia-camera-sc51g-test.apk`。ローカル署名鍵は初回ビルド時に `keys/port-test.jks` に生成されます。過去に配布したv0.2のAPKとは鍵が異なるため、そのまま上書き更新はできません。

色計算の再実行にはNumPyとPillow、および [色処理の説明](COLOR-PROCESSING.md) に記載の参照画像を `analysis/color-reference/galaxy-chart.jpg` と `analysis/color-reference/xperia-chart.jpg` に用意し、`python tools/fit-color-reference.py` を実行してください。参照画像そのものは含めていません。

## 公開物について

Sony / Samsungの公式プロジェクトではありません。提供APKを土台にした互換性の試作であり、Sony純正ISPの移植や全機能の動作を保証するものではありません。Sony由来のアプリ本体・名称・画像・音源などの権利は元の権利者に帰属します。本リポジトリはそれらに新しい利用許諾を与えるものではありません。

秘密鍵、端末の接続情報、実機ログ、テスト写真・動画、展開済みの元コードは含めていません。APKは配布しません（[配布方針](#配布方針)）。網羅的なデバッグは行っていません。

参考：[Android公式 Multi-camera API](https://developer.android.com/media/camera/camera2/multi-camera)、[ドコモ SC-51G仕様](https://www.docomo.ne.jp/product/sc51g/spec.html)。

---

<a id="english"></a>

## English

**Bring the Xperia camera UI to Galaxy S26. Zoom with the volume keys and adjust color and shutter sound.**

![Distribution](https://img.shields.io/badge/Distribution-Source_only-blue)
![Device](https://img.shields.io/badge/Galaxy_S26-SC--51G-1428A0)
![Status](https://img.shields.io/badge/Status-Experimental-orange)

An unofficial project exploring the Xperia camera interface on Galaxy S26. It provides rear 0.6× / 1× / 3× zoom presets, volume-key zoom, adjustable shutter sound, warm/cool controls and experimental color correction for saved photos.

→ **No APK is distributed.** [Build it yourself](#building-locally) · [Distribution policy](#distribution-policy) · [Color-processing details (Japanese)](COLOR-PROCESSING.md)

### v0.2: Color controls

The warm/cool calculation found in the supplied APK is now connected to standard Camera2 controls. A new **「色」 (Color)** button provides photo correction derived from published comparison charts. This optional correction is **off by default**. **No prebuilt APK is distributed**; the repository publishes the sources, patches and build scripts, and you build it yourself (see [Distribution policy](#distribution-policy)). See [COLOR-PROCESSING.md (Japanese)](COLOR-PROCESSING.md) for sources, measurements and implementation details. This project does not port Sony's complete imaging engine. The device results below were obtained from a build made on 2026-11-03.

The tested device is **Galaxy S26 SC-51G, Android 17 (API 37) / One UI 9**. The input is `camera-2-9-a-0-24.apk`, package `com.sonyericsson.android.camera`, displayed version `2.9.A.0.24`. The input file is preserved unchanged. It already contained modifications, including fixed camera IDs and zoom changes; it has not been verified as an untouched official Sony binary.

### Building and installing

No APK is distributed. You install a build you make yourself; see [Building locally](#building-locally) for the full procedure.

1. Obtain a matching `camera-2-9-a-0-24.apk` and place it in the repository root.
2. Run `setup-port.ps1` then `build-port.ps1` on Windows, or `setup-port.sh` then `build-port.sh` on Linux / macOS.
3. Copy `out/xperia-camera-sc51g-test.apk` to the phone and install it.
4. Launch the app and grant the camera, microphone and other permissions needed for capture.

Installation may fail if another app with the package name `com.sonyericsson.android.camera` is installed with a different signature. A local build generates `keys/port-test.jks` on first use and signs with that key, so it cannot update an installation of the APK previously published as v0.2.

For reference only: the SHA-256 of the v0.2 APK that was published on 2026-11-03 is `155c4b3474ac8034cb5fe94a766b3ec0bf253702d4d192d3bce15de665628b0f`. It is kept so that copies already downloaded can be checked; it is no longer distributed.

### Controls

- **Zoom presets:** 0.6×, 1× and 3×. Rear zoom is clamped to the device's exposed range of 0.6–10×.
- **Volume + / −:** zoom in / out, retaining the zoom-key behavior in the supplied APK.
- **Speaker button in the top shortcut row:** enable or mute shutter sound, adjust its level from 1–100%, and preview it. Settings persist. Playback also follows the phone's media volume.
- **Shortcut placement:** the new buttons share the existing flash/timer row. The layout was adjusted to keep the toolbar visible below screen insets.
- **「色」 (Color) button:** toggle Web comparison correction and set its strength from 0–100%. Defaults are off and 35% strength. It affects saved JPEG photos only, leaving preview and video unaffected by this correction. Enabling it recompresses the JPEG.
- **Save location:** `DCIM/Camera` for photos and videos.

### Verified on the device

The following checks were performed on the connected SC-51G on **November 3, 2026**.

| Item | Observed result |
| --- | --- |
| Launch and live preview | Working |
| Rear ultrawide | Physical sensor ID 2, focal length 2.2 mm |
| Rear wide | Physical sensor ID 5, focal length 5.4 mm |
| Rear telephoto | Physical sensor ID 6, focal length 7.0 mm at approximately 3× |
| Front camera switching | Preview obtained with a 3.3 mm focal length |
| Volume keys | 1.0165× → volume +: 1.1408× → volume −: 1.0165× |
| Photo capture | 4000 × 3000 JPEG saved |
| Muted photo capture | A new JPEG saved with shutter sound muted |
| Video | 1920 × 1080 MP4 saved, approximately 5.5 seconds |
| Shutter sound | SoundPool playback at the selected gain, mute switching and persistent settings verified |
| Settings screen | Opens and returns to capture after hiding settings with no available options |
| APK | Rebuilt, ZIP-aligned for 16 KB pages, signature verified and installed on the device |

Samsung's camera driver selects the physical lens for the requested zoom. In low light or at certain subject distances, a 3× request may use a crop from the wide camera. This implementation does not force the telephoto lens at every 3× request.

### Main changes

- Made the Sony shared-library dependency optional.
- Replaced Sony-oriented fixed camera IDs such as 3/4 with SC-51G's rear logical camera 0 and front camera 1.
- Used standard `CONTROL_ZOOM_RATIO` to access ultrawide, wide and telephoto cameras under the rear logical camera.
- Read maximum zoom, exposure-time range and physical-camera availability from standard Camera2 capabilities.
- Filtered out Sony-specific session and request keys, and avoided crashes when reading unsupported request keys.
- Bypassed Sony's virtual JPEG postprocessing camera and used standard JPEG capture instead.
- Used standard AF mode, AE mode and AF regions to check autofocus-setting reflection.
- Hid settings whose filtered option lists are empty.
- Stored the added sound-level setting within the app without changing system volume. Shutter sound uses audio from the supplied APK; video start/stop sounds retain their original playback path.

### Scope and limitations

This is a prototype port for running the supplied camera app on Galaxy. Its interface is based on that APK; sensor processing and image generation use Samsung's publicly accessible camera path. It does not reproduce Sony's image processing or guarantee equivalent image quality.

- **50 MP capture, RAW saving and advanced Samsung stock-camera-only processing are not implemented.** Verified still photos are 12 MP.
- Sony-specific HDR, scene recognition, background processing and special capture features have not been equivalently ported.
- The standard Camera2 path for specifying both ISO and shutter speed remains, but image output and accuracy across all manual settings are unverified. ISO-priority and shutter-priority automatic control relying on Qualcomm-specific tags in the original APK is not guaranteed to work.
- **4K, high frame rates, slow motion, long recordings and all shooting conditions are unverified.**
- Web comparison correction is an experiment based on published charts from different devices. It is not a calibration of SC-51G or a reproduction of Sony's color science. The reference Galaxy used Exynos hardware, unlike the target SC-51G. The comparison does not establish an improvement across real-world scenes.
- Device tests saved 4000 × 3000 JPEGs with correction at 35%; the measured extra processing time was approximately 215–291 ms. Decoding and EXIF orientation retention were checked. Warm/cool adjustments were also checked for repeated changes without accumulating the correction and for return to automatic white balance.
- Test photos and short videos on the device were not automatically deleted.

### Distribution policy

This repository **does not distribute an APK**. What is published here is the patch set, the added code, the build scripts and the test record.

Redistributing a modified, re-signed APK to the public goes beyond the permission the rights holders granted for Sony-derived app code, sounds and images. The APK published as v0.2 was therefore withdrawn on 2026-11-07. For the same reason, mirrors and re-uploads of built APKs are not provided.

- Build it yourself, on your own device, from a matching APK you obtained legitimately (see [Building locally](#building-locally)).
- Keep any build you make for your own device and do not redistribute it.
- Only the compatibility diff and prototype code live here. This is not an official Sony or Samsung project.

### Building locally

Requirements: **JDK 17, Python 3, Android SDK** (`platforms/android-35` and `build-tools/36.0.0`), and [Apktool 3.0.3](https://github.com/iBotPeaches/Apktool/releases/tag/v3.0.3). Place its JAR at `tools/apktool.jar`. The scripts locate the SDK through `ANDROID_SDK_ROOT`, `ANDROID_HOME`, or the platform default (`%LOCALAPPDATA%\Android\Sdk` on Windows, `~/Library/Android/sdk` on macOS, `~/Android/Sdk` on Linux).

The input APK is not included in this repository. Place an appropriately obtained matching `camera-2-9-a-0-24.apk` in the project root. Patching other versions is unsupported.

Input APK SHA-256: `04a7b4c30259ab0cc1466addf38a6be5dff904b74f8c40cf4e60551a50386d7c`.

```powershell
.\setup-port.ps1
.\build-port.ps1
```

```bash
./setup-port.sh
./build-port.sh
```

The PowerShell scripts are the ones used for the verified device builds. The Linux / macOS scripts are a port of the same steps and were not executed in this project's verification environment.

`src/` contains the added controls, sound handling and color processing; `patches/` contains Camera2 compatibility helpers; `tools/patch_port.py` modifies the decoded code. The output is `out/xperia-camera-sc51g-test.apk`.

A local signing key is generated at `keys/port-test.jks` on the first build. It differs from the key of the v0.2 APK that was previously published, so a local build cannot directly update an existing installation of it.

To rerun the color fit, install NumPy and Pillow and obtain the reference images linked in [COLOR-PROCESSING.md](COLOR-PROCESSING.md). Save them as `analysis/color-reference/galaxy-chart.jpg` and `analysis/color-reference/xperia-chart.jpg`, then run `python tools/fit-color-reference.py`. The reference images themselves are not included.

### About this repository

This is **not an official Sony or Samsung project**. It is a compatibility prototype based on a supplied APK; it does not guarantee a Sony ISP port or complete feature support. Rights to Sony-derived app components, names, images and sounds remain with their respective owners. This repository does not grant a new license to those materials.

The repository excludes private signing keys, device connection information, device logs, test photos/videos and the decoded original code. No APK is distributed (see [Distribution policy](#distribution-policy)). Comprehensive debugging has not been performed.

References: [Android Multi-camera API](https://developer.android.com/media/camera/camera2/multi-camera), [NTT DOCOMO SC-51G specifications (Japanese)](https://www.docomo.ne.jp/product/sc51g/spec.html).

[Back to language selection](#languages)
