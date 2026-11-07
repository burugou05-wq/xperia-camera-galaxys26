#!/usr/bin/env bash
# Compiles src/local/sc51g into a small helper APK and copies its smali into ./decoded.
# Called by build-port.sh; you normally do not need to run it on its own.
set -euo pipefail
cd "$(dirname "$0")"

sdk="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-}}"
if [[ -z $sdk ]]; then
  for candidate in "$HOME/Library/Android/sdk" "$HOME/Android/Sdk"; do
    if [[ -d $candidate ]]; then sdk=$candidate; break; fi
  done
fi
[[ -n $sdk && -d $sdk ]] || { echo 'Android SDK not found; set ANDROID_SDK_ROOT or ANDROID_HOME.' >&2; exit 1; }

android_jar="$sdk/platforms/android-35/android.jar"
build_tools="$sdk/build-tools/36.0.0"
python="${PYTHON:-python3}"

[[ -f $android_jar ]] || { echo "Missing $android_jar" >&2; exit 1; }
[[ -x $build_tools/d8 ]] || { echo "Missing $build_tools/d8" >&2; exit 1; }
[[ -f tools/apktool.jar ]] || { echo 'Place Apktool at tools/apktool.jar.' >&2; exit 1; }

mkdir -p build/helper/classes build/helper/dex
javac -encoding UTF-8 -source 8 -target 8 -classpath "$android_jar" \
  -d build/helper/classes src/local/sc51g/*.java
"$python" tools/package-helper.py classes
"$build_tools/d8" --lib "$android_jar" --min-api 31 \
  --output build/helper/dex build/helper/classes.jar
"$python" tools/package-helper.py
java -jar tools/apktool.jar d -r -f build/helper/helper.apk \
  -o build/helper/decoded -p tools/framework
mkdir -p decoded/smali
cp -R build/helper/decoded/smali/local decoded/smali/
