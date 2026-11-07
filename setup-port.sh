#!/usr/bin/env bash
# Step 1: decode the input APK into ./decoded (never modifies the input file).
set -euo pipefail
cd "$(dirname "$0")"

input='camera-2-9-a-0-24.apk'

[[ -f $input ]] || { echo "Place the matching input APK ($input) in the project root." >&2; exit 1; }
[[ ! -e decoded ]] || { echo 'decoded already exists; keep your current work or use a fresh checkout.' >&2; exit 1; }
[[ -f tools/apktool.jar ]] || { echo 'Place Apktool at tools/apktool.jar.' >&2; exit 1; }

java -jar tools/apktool.jar d "$input" -o decoded -p tools/framework
