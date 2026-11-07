#!/usr/bin/env bash
# Step 2: build the helper, apply patches, rebuild, align for 16 KB pages, sign and verify.
set -euo pipefail
cd "$(dirname "$0")"

[[ -d decoded ]] || { echo 'Run ./setup-port.sh first.' >&2; exit 1; }

sdk="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-}}"
if [[ -z $sdk ]]; then
  for candidate in "$HOME/Library/Android/sdk" "$HOME/Android/Sdk"; do
    if [[ -d $candidate ]]; then sdk=$candidate; break; fi
  done
fi
[[ -n $sdk && -d $sdk ]] || { echo 'Android SDK not found; set ANDROID_SDK_ROOT or ANDROID_HOME.' >&2; exit 1; }

build_tools="$sdk/build-tools/36.0.0"
python="${PYTHON:-python3}"
[[ -x $build_tools/zipalign && -x $build_tools/apksigner ]] || {
  echo "Missing zipalign or apksigner in $build_tools" >&2; exit 1; }
[[ -f tools/apktool.jar ]] || { echo 'Place Apktool at tools/apktool.jar.' >&2; exit 1; }

mkdir -p out keys
./build-helper.sh
"$python" tools/patch_port.py

java -jar tools/apktool.jar b decoded -p tools/framework -o out/camera-unsigned.apk

if [[ ! -f keys/port-test.jks ]]; then
  keytool -genkeypair -keystore keys/port-test.jks -storepass android -keypass android \
    -alias port -keyalg RSA -keysize 3072 -validity 10000 \
    -dname 'CN=SC-51G Camera Port Test'
fi

"$build_tools/zipalign" -f -P 16 4 out/camera-unsigned.apk out/camera-aligned.apk
"$build_tools/apksigner" sign --ks keys/port-test.jks --ks-key-alias port \
  --ks-pass pass:android --key-pass pass:android \
  --out out/xperia-camera-sc51g-test.apk out/camera-aligned.apk
"$build_tools/apksigner" verify --verbose out/xperia-camera-sc51g-test.apk

echo 'Built out/xperia-camera-sc51g-test.apk'
