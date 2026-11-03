$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$sdkPath = $env:ANDROID_SDK_ROOT
if (!$sdkPath) { $sdkPath = $env:ANDROID_HOME }
if (!$sdkPath) { $sdkPath = Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$androidJar = Join-Path $sdkPath 'platforms\android-35\android.jar'
$buildTools = Join-Path $sdkPath 'build-tools\36.0.0'
New-Item -ItemType Directory -Force -Path 'build/helper/classes','build/helper/dex' | Out-Null
javac -encoding UTF-8 -source 8 -target 8 -classpath $androidJar -d '.\build\helper\classes' (Get-ChildItem -LiteralPath '.\src\local\sc51g' -Filter '*.java' | ForEach-Object FullName)
if ($LASTEXITCODE -ne 0) { throw 'Sound control compilation failed' }
python '.\tools\package-helper.py' classes
if ($LASTEXITCODE -ne 0) { throw 'Helper archive failed' }
& "$buildTools\d8.bat" --lib $androidJar --min-api 31 --output '.\build\helper\dex' '.\build\helper\classes.jar'
if ($LASTEXITCODE -ne 0) { throw 'Helper conversion failed' }
python '.\tools\package-helper.py'
if ($LASTEXITCODE -ne 0) { throw 'Helper packaging failed' }
java -jar '.\tools\apktool.jar' d -r -f '.\build\helper\helper.apk' -o '.\build\helper\decoded' -p '.\tools\framework'
if ($LASTEXITCODE -ne 0) { throw 'Helper disassembly failed' }
Copy-Item -Path '.\build\helper\decoded\smali\local' -Destination '.\decoded\smali' -Recurse -Force
