$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$sdkPath = $env:ANDROID_SDK_ROOT
if (!$sdkPath) { $sdkPath = $env:ANDROID_HOME }
if (!$sdkPath) { $sdkPath = Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$buildTools = Join-Path $sdkPath 'build-tools\36.0.0'
New-Item -ItemType Directory -Force -Path 'out','keys' | Out-Null
& '.\build-helper.ps1'
python '.\tools\patch_port.py'
if ($LASTEXITCODE -ne 0) { throw 'Patch failed' }
java -jar '.\tools\apktool.jar' b '.\decoded' -p '.\tools\framework' -o '.\out\camera-unsigned.apk'
if ($LASTEXITCODE -ne 0) { throw 'APK build failed' }
if (!(Test-Path -LiteralPath '.\keys\port-test.jks')) {
    keytool -genkeypair -keystore '.\keys\port-test.jks' -storepass android -keypass android -alias port -keyalg RSA -keysize 3072 -validity 10000 -dname 'CN=SC-51G Camera Port Test'
    if ($LASTEXITCODE -ne 0) { throw 'Test key generation failed' }
}
& "$buildTools\zipalign.exe" -f -P 16 4 '.\out\camera-unsigned.apk' '.\out\camera-aligned.apk'
if ($LASTEXITCODE -ne 0) { throw 'APK alignment failed' }
& "$buildTools\apksigner.bat" sign --ks '.\keys\port-test.jks' --ks-key-alias port --ks-pass pass:android --key-pass pass:android --out '.\out\xperia-camera-sc51g-test.apk' '.\out\camera-aligned.apk'
if ($LASTEXITCODE -ne 0) { throw 'APK signing failed' }
& "$buildTools\apksigner.bat" verify --verbose '.\out\xperia-camera-sc51g-test.apk'
if ($LASTEXITCODE -ne 0) { throw 'APK signature verification failed' }
