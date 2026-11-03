$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (!(Test-Path -LiteralPath '.\camera-2-9-a-0-24.apk')) { throw 'Place the matching input APK in the project root.' }
if (Test-Path -LiteralPath '.\decoded') { throw 'decoded already exists; keep your current work or use a fresh checkout.' }
java -jar '.\tools\apktool.jar' d '.\camera-2-9-a-0-24.apk' -o '.\decoded' -p '.\tools\framework'
if ($LASTEXITCODE -ne 0) { throw 'APK decoding failed' }
