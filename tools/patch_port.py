"""Reproducible patches for the supplied Xperia camera APK (never edits input APK)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DECODED = ROOT / 'decoded'

def replace_method(relative, signature, body):
    path = DECODED / 'smali' / relative
    source = path.read_text(encoding='utf-8')
    pattern = r'(?m)^\.method [^\n]*' + re.escape(signature) + r'\n.*?^\.end method'
    source, count = re.subn(pattern, lambda m: m.group(0).splitlines()[0] + '\n' + body.strip('\n') + '\n.end method', source, flags=re.S|re.M)
    if count != 1:
        raise ValueError(f'{relative}: expected one {signature}, found {count}')
    if source != path.read_text(encoding='utf-8'):
        path.write_text(source, encoding='utf-8')

def edit_method(relative, signature, transform):
    path = DECODED / 'smali' / relative
    source = path.read_text(encoding='utf-8')
    pattern = r'(?m)^\.method [^\n]*' + re.escape(signature) + r'\n.*?^\.end method'
    patched, count = re.subn(pattern, lambda m: transform(m.group(0)), source, flags=re.S|re.M)
    assert count == 1, (relative, signature, count)
    if patched != source:
        path.write_text(patched, encoding='utf-8')

def main():
    manifest = DECODED / 'AndroidManifest.xml'
    text = manifest.read_text(encoding='utf-8')
    text = text.replace('android:name="com.sony.device" android:required="true"', 'android:name="com.sony.device" android:required="false"')
    text = text.replace('android:extractNativeLibs="false"', 'android:extractNativeLibs="true"')
    if text != manifest.read_text(encoding='utf-8'):
        manifest.write_text(text, encoding='utf-8')

    cap = 'com/sonyericsson/android/camera/util/capability/'
    edit_method('com/sonyericsson/android/camera/CameraApplication.smali', 'onCreate()V',
        lambda method: method if 'ColorPipeline;->initialize' in method else re.sub(r'(    \.locals \d+)', r'\1\n    invoke-static {p0}, Llocal/sc51g/ColorPipeline;->initialize(Landroid/content/Context;)V', method, count=1))
    for name, sign in [('getMaxAwbColorCompensationAb', ''), ('getMinAwbColorCompensationAb', '    neg-int v0, v0\n')]:
        replace_method(cap + 'CameraStaticParameters.smali', name+'()I', '''
    .locals 1
    iget-object v0, p0, Lcom/sonyericsson/android/camera/util/capability/CameraStaticParameters;->mCharacteristics:Landroid/hardware/camera2/CameraCharacteristics;
    invoke-static {v0}, Llocal/sc51g/ColorPipeline;->warmthLimit(Landroid/hardware/camera2/CameraCharacteristics;)I
    move-result v0
''' + sign + '    return v0')
    replace_method('com/sonyericsson/android/camera/device/CameraController.smali', 'applyAmberBlueColor(Lcom/sonyericsson/android/camera/device/CameraParameters;)V', '''
    .locals 5
    const/16 v0, -0x64
    const/4 v1, 0x0
    invoke-static {v0, v1}, Llocal/sc51g/ColorPipeline;->requestWarmth(ILandroid/hardware/camera2/params/RggbChannelVector;)V
    invoke-virtual {p1}, Lcom/sonyericsson/android/camera/device/CameraParameters;->getWhiteBalance()Ljava/lang/String;
    move-result-object v0
    const-string v1, "auto"
    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :done
    iget-object v0, p0, Lcom/sonyericsson/android/camera/device/CameraController;->mCaptureRequestHolder:Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;
    sget-object v1, Landroid/hardware/camera2/CaptureRequest;->CONTROL_AWB_MODE:Landroid/hardware/camera2/CaptureRequest$Key;
    const/4 v2, 0x1
    invoke-static {v2}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v2
    invoke-virtual {v0, v1, v2}, Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;->set(Landroid/hardware/camera2/CaptureRequest$Key;Ljava/lang/Object;)V
    invoke-virtual {p1}, Lcom/sonyericsson/android/camera/device/CameraParameters;->getAwbColorCompensationAb()I
    move-result v0
    const/16 v1, -0x64
    if-eq v0, v1, :done
    if-eqz v0, :done
    iget-object v1, p0, Lcom/sonyericsson/android/camera/device/CameraController;->mCurrentAwbColorValue:Landroid/hardware/camera2/params/RggbChannelVector;
    if-eqz v1, :done
    invoke-direct {p0, v0}, Lcom/sonyericsson/android/camera/device/CameraController;->getAwbColorCompensationRggbVector(I)Landroid/hardware/camera2/params/RggbChannelVector;
    move-result-object v1
    invoke-static {v0, v1}, Llocal/sc51g/ColorPipeline;->requestWarmth(ILandroid/hardware/camera2/params/RggbChannelVector;)V
    :done
    return-void
''')
    replace_method('com/sonyericsson/android/camera/device/CameraController.smali', 'updateAwbColorValue(Landroid/hardware/camera2/TotalCaptureResult;)V', '''
    .locals 2
    sget-object v0, Landroid/hardware/camera2/CaptureResult;->CONTROL_AWB_MODE:Landroid/hardware/camera2/CaptureResult$Key;
    invoke-virtual {p1, v0}, Landroid/hardware/camera2/TotalCaptureResult;->get(Landroid/hardware/camera2/CaptureResult$Key;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Ljava/lang/Integer;
    if-eqz v0, :done
    invoke-virtual {v0}, Ljava/lang/Integer;->intValue()I
    move-result v0
    const/4 v1, 0x1
    if-ne v0, v1, :done
    sget-object v0, Landroid/hardware/camera2/CaptureResult;->COLOR_CORRECTION_GAINS:Landroid/hardware/camera2/CaptureResult$Key;
    invoke-virtual {p1, v0}, Landroid/hardware/camera2/TotalCaptureResult;->get(Landroid/hardware/camera2/CaptureResult$Key;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/hardware/camera2/params/RggbChannelVector;
    if-eqz v0, :done
    iput-object v0, p0, Lcom/sonyericsson/android/camera/device/CameraController;->mCurrentAwbColorValue:Landroid/hardware/camera2/params/RggbChannelVector;
    :done
    return-void
''')
    edit_method('com/sonyericsson/android/camera/device/CameraController$CameraStateCallback.smali', 'onOpened(Landroid/hardware/camera2/CameraDevice;)V',
        lambda method: method if 'ColorPipeline;->reset' in method else re.sub(r'(    \.locals \d+)', r'\1\n    invoke-static {}, Llocal/sc51g/ColorPipeline;->reset()V', method, count=1))
    holder = DECODED / 'smali/com/sonyericsson/android/camera/device/CaptureRequestHolder.smali'
    source = holder.read_text(encoding='utf-8')
    if 'ColorPipeline;->prepare' not in source:
        source, count = re.subn(r'(    invoke-virtual \{([vp]\d+)\}, Landroid/hardware/camera2/CaptureRequest\$Builder;->build\(\)Landroid/hardware/camera2/CaptureRequest;)',
            r'    invoke-static {\2}, Llocal/sc51g/ColorPipeline;->prepare(Landroid/hardware/camera2/CaptureRequest$Builder;)V\n\1', source)
        assert count == 4, count
        holder.write_text(source, encoding='utf-8')
    def process_jpeg(method):
        if 'ColorPipeline;->processJpeg' in method: return method
        needle='    invoke-virtual {v0}, Landroid/media/Image;->close()V'
        assert method.count(needle)==1
        return method.replace(needle, needle+'\n    invoke-static {v5}, Llocal/sc51g/ColorPipeline;->processJpeg([B)[B\n    move-result-object v5')
    edit_method('com/sonyericsson/android/camera/device/CameraController$CaptureRequestCallback.smali', 'checkCaptureDone()V', process_jpeg)
    # During the port, always refresh hardware metadata rather than reusing Sony-era caches.
    for method in [
        'loadCameraCapabilityFromPreferences(Landroid/content/Context;Lcom/sonyericsson/android/camera/device/CameraInfo$CameraId;)Lcom/sonyericsson/android/camera/util/capability/CameraCapabilityList;',
        'loadPlatformCapabilityFromPreferences(Landroid/content/Context;)Lcom/sonyericsson/android/camera/util/capability/PlatformCapabilityList;'
    ]:
        replace_method(cap + 'PlatformCapability.smali', method, '    .locals 1\n    const/4 v0, 0x0\n    return-object v0')
    # Samsung's rear logical camera owns ultra-wide, main and telephoto sensors.
    # Never open Sony's fixed IDs 3/4 (front/system-only cameras on this device).
    entries = {'BACK': '0', 'FRONT': '1', 'U_WIDE': '0', 'TELE': '0', 'SAT': '0', 'BOKEH': '0'}
    body = ['    .locals 3', '    new-instance v0, Ljava/util/HashMap;',
            '    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V']
    for name, device_id in entries.items():
        body += [f'    sget-object v1, Lcom/sonyericsson/android/camera/device/CameraInfo$CameraId;->{name}:Lcom/sonyericsson/android/camera/device/CameraInfo$CameraId;',
                 f'    const-string v2, "{device_id}"',
                 '    invoke-interface {v0, v1, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;']
    body += ['    return-object v0']
    replace_method(cap + 'PlatformCapabilityList.smali', 'initializeCameraIdsPairing(Landroid/content/Context;)Ljava/util/Map;', '\n'.join(body))
    replace_method(cap + 'PlatformCapability.smali', 'checkProduct()V', '''
    .locals 1
    sget-object v0, Lcom/sonyericsson/android/camera/util/capability/PlatformCapability$Product;->NONE:Lcom/sonyericsson/android/camera/util/capability/PlatformCapability$Product;
    sput-object v0, Lcom/sonyericsson/android/camera/util/capability/PlatformCapability;->sProduct:Lcom/sonyericsson/android/camera/util/capability/PlatformCapability$Product;
    return-void
''')
    replace_method(cap + 'CameraStaticParameters.smali', 'getMaxZoomRatio()F', '''
    .locals 2
    iget-object v0, p0, Lcom/sonyericsson/android/camera/util/capability/CameraStaticParameters;->mCharacteristics:Landroid/hardware/camera2/CameraCharacteristics;
    sget-object v1, Landroid/hardware/camera2/CameraCharacteristics;->CONTROL_ZOOM_RATIO_RANGE:Landroid/hardware/camera2/CameraCharacteristics$Key;
    invoke-virtual {v0, v1}, Landroid/hardware/camera2/CameraCharacteristics;->get(Landroid/hardware/camera2/CameraCharacteristics$Key;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/util/Range;
    invoke-virtual {v0}, Landroid/util/Range;->getUpper()Ljava/lang/Comparable;
    move-result-object v0
    check-cast v0, Ljava/lang/Float;
    invoke-virtual {v0}, Ljava/lang/Float;->floatValue()F
    move-result v0
    return v0
''')
    replace_method(cap + 'CameraStaticParameters.smali', 'isOpticalZoomSupported()Z', '''
    .locals 2
    iget-object v0, p0, Lcom/sonyericsson/android/camera/util/capability/CameraStaticParameters;->mCharacteristics:Landroid/hardware/camera2/CameraCharacteristics;
    invoke-virtual {v0}, Landroid/hardware/camera2/CameraCharacteristics;->getPhysicalCameraIds()Ljava/util/Set;
    move-result-object v0
    invoke-interface {v0}, Ljava/util/Set;->size()I
    move-result v0
    const/4 v1, 0x1
    if-gt v0, v1, :supported
    const/4 v1, 0x0
    :supported
    return v1
''')
    controller = 'com/sonyericsson/android/camera/device/CameraController.smali'
    replace_method(controller, 'applyZoom(Lcom/sonyericsson/android/camera/device/CameraParameters;)V', '''
    .locals 6
    invoke-virtual {p1}, Lcom/sonyericsson/android/camera/device/CameraParameters;->getCameraId()Lcom/sonyericsson/android/camera/device/CameraInfo$CameraId;
    move-result-object v0
    invoke-static {v0}, Lcom/sonyericsson/android/camera/util/capability/PlatformCapability;->getMaxZoomRatio(Lcom/sonyericsson/android/camera/device/CameraInfo$CameraId;)F
    move-result v1
    invoke-virtual {p1}, Lcom/sonyericsson/android/camera/device/CameraParameters;->getZoom()F
    move-result v2
    const/high16 v3, 0x3f800000
    sub-float v4, v1, v3
    mul-float/2addr v2, v4
    add-float/2addr v2, v3
    invoke-virtual {v0}, Lcom/sonyericsson/android/camera/device/CameraInfo$CameraId;->isFront()Z
    move-result v4
    if-nez v4, :clamp
    const v3, 0x3f19999a
    :clamp
    invoke-static {v2, v3}, Ljava/lang/Math;->max(FF)F
    move-result v2
    invoke-static {v2, v1}, Ljava/lang/Math;->min(FF)F
    move-result v2
    iget-object v4, p0, Lcom/sonyericsson/android/camera/device/CameraController;->mCaptureRequestHolder:Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;
    sget-object v5, Landroid/hardware/camera2/CaptureRequest;->CONTROL_ZOOM_RATIO:Landroid/hardware/camera2/CaptureRequest$Key;
    invoke-static {v2}, Ljava/lang/Float;->valueOf(F)Ljava/lang/Float;
    move-result-object v2
    invoke-virtual {v4, v5, v2}, Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;->set(Landroid/hardware/camera2/CaptureRequest$Key;Ljava/lang/Object;)V
    invoke-static {v0}, Lcom/sonyericsson/android/camera/util/capability/PlatformCapability;->getActiveArraySize(Lcom/sonyericsson/android/camera/device/CameraInfo$CameraId;)Landroid/graphics/Rect;
    move-result-object v0
    sget-object v5, Landroid/hardware/camera2/CaptureRequest;->SCALER_CROP_REGION:Landroid/hardware/camera2/CaptureRequest$Key;
    invoke-virtual {v4, v5, v0}, Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;->set(Landroid/hardware/camera2/CaptureRequest$Key;Ljava/lang/Object;)V
    return-void
''')
    replace_method(controller, 'applyDisableBGProcess(Lcom/sonyericsson/android/camera/device/CameraParameters;)V', '''
    .locals 0
    return-void
''')
    replace_method('com/sonyericsson/android/camera/device/AfParametersReflectedChecker.smali', 'checkSync(Landroid/hardware/camera2/CaptureResult;)Z', '''
    .locals 5
    const/4 v4, 0x0
    if-eqz p1, :done
    iget-object v0, p0, Lcom/sonyericsson/android/camera/device/AfParametersReflectedChecker;->mReqHolder:Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;
    sget-object v1, Landroid/hardware/camera2/CaptureRequest;->CONTROL_AF_MODE:Landroid/hardware/camera2/CaptureRequest$Key;
    invoke-virtual {v0, v1}, Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;->get(Landroid/hardware/camera2/CaptureRequest$Key;)Ljava/lang/Object;
    move-result-object v1
    sget-object v2, Landroid/hardware/camera2/CaptureResult;->CONTROL_AF_MODE:Landroid/hardware/camera2/CaptureResult$Key;
    invoke-virtual {p1, v2}, Landroid/hardware/camera2/CaptureResult;->get(Landroid/hardware/camera2/CaptureResult$Key;)Ljava/lang/Object;
    move-result-object v2
    invoke-static {v1, v2}, Ljava/util/Objects;->equals(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :done
    sget-object v1, Landroid/hardware/camera2/CaptureRequest;->CONTROL_AE_MODE:Landroid/hardware/camera2/CaptureRequest$Key;
    invoke-virtual {v0, v1}, Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;->get(Landroid/hardware/camera2/CaptureRequest$Key;)Ljava/lang/Object;
    move-result-object v1
    sget-object v2, Landroid/hardware/camera2/CaptureResult;->CONTROL_AE_MODE:Landroid/hardware/camera2/CaptureResult$Key;
    invoke-virtual {p1, v2}, Landroid/hardware/camera2/CaptureResult;->get(Landroid/hardware/camera2/CaptureResult$Key;)Ljava/lang/Object;
    move-result-object v2
    invoke-static {v1, v2}, Ljava/util/Objects;->equals(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :done
    sget-object v1, Landroid/hardware/camera2/CaptureRequest;->CONTROL_AF_REGIONS:Landroid/hardware/camera2/CaptureRequest$Key;
    invoke-virtual {v0, v1}, Lcom/sonyericsson/android/camera/device/CaptureRequestHolder;->get(Landroid/hardware/camera2/CaptureRequest$Key;)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, [Landroid/hardware/camera2/params/MeteringRectangle;
    if-eqz v1, :matched
    sget-object v2, Landroid/hardware/camera2/CaptureResult;->CONTROL_AF_REGIONS:Landroid/hardware/camera2/CaptureResult$Key;
    invoke-virtual {p1, v2}, Landroid/hardware/camera2/CaptureResult;->get(Landroid/hardware/camera2/CaptureResult$Key;)Ljava/lang/Object;
    move-result-object v2
    check-cast v2, [Landroid/hardware/camera2/params/MeteringRectangle;
    invoke-static {v1, v2}, Ljava/util/Arrays;->equals([Ljava/lang/Object;[Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :done
    :matched
    const/4 v4, 0x1
    :done
    return v4
''')
    # Sony represents exposure bounds as long[2], Android represents them as Range<Long>.
    static_path = DECODED / 'smali' / cap / 'CameraStaticParameters.smali'
    source = static_path.read_text(encoding='utf-8')
    prefix = 'Lcom/sonyericsson/android/camera/util/capability/CameraStaticParameters;'
    source = re.sub(r'sget-object (v\d+), Lcom/sonyericsson/android/camera/device/SomcCameraCharacteristicsKeys;->SONYMOBILE_SENSOR_INFO_EXPOSURE_TIME_RANGE:Landroid/hardware/camera2/CameraCharacteristics\$Key;\s+invoke-direct \{p0, \1\}, ' + re.escape(prefix) + r'->tryGetCharacteristics\(Landroid/hardware/camera2/CameraCharacteristics\$Key;\)Ljava/lang/Object;',
                    'invoke-direct {p0}, ' + prefix + '->getGalaxyExposureRange()[J', source)
    if '.method private getGalaxyExposureRange()[J' not in source:
        source += '''
.method private getGalaxyExposureRange()[J
    .locals 6
    iget-object v0, p0, Lcom/sonyericsson/android/camera/util/capability/CameraStaticParameters;->mCharacteristics:Landroid/hardware/camera2/CameraCharacteristics;
    sget-object v1, Landroid/hardware/camera2/CameraCharacteristics;->SENSOR_INFO_EXPOSURE_TIME_RANGE:Landroid/hardware/camera2/CameraCharacteristics$Key;
    invoke-virtual {v0, v1}, Landroid/hardware/camera2/CameraCharacteristics;->get(Landroid/hardware/camera2/CameraCharacteristics$Key;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/util/Range;
    if-nez v0, :range
    const/4 v0, 0x0
    return-object v0
    :range
    const/4 v1, 0x2
    new-array v1, v1, [J
    invoke-virtual {v0}, Landroid/util/Range;->getLower()Ljava/lang/Comparable;
    move-result-object v2
    check-cast v2, Ljava/lang/Long;
    invoke-virtual {v2}, Ljava/lang/Long;->longValue()J
    move-result-wide v2
    const/4 v4, 0x0
    aput-wide v2, v1, v4
    invoke-virtual {v0}, Landroid/util/Range;->getUpper()Ljava/lang/Comparable;
    move-result-object v2
    check-cast v2, Ljava/lang/Long;
    invoke-virtual {v2}, Ljava/lang/Long;->longValue()J
    move-result-wide v2
    const/4 v4, 0x1
    aput-wide v2, v1, v4
    return-object v1
.end method
'''
    if source != static_path.read_text(encoding='utf-8'):
        static_path.write_text(source, encoding='utf-8')

    for name in ['GalaxyTelemetry', 'GalaxyCamera']:
        destination = DECODED / f'smali/local/sc51g/{name}.smali'
        destination.parent.mkdir(parents=True, exist_ok=True)
        template = (ROOT / f'patches/{name}.smali').read_text(encoding='utf-8')
        if not destination.exists() or destination.read_text(encoding='utf-8') != template:
            destination.write_text(template, encoding='utf-8')
    for path in (DECODED / 'smali/com/sonyericsson').rglob('*.smali'):
        source = path.read_text(encoding='utf-8')
        patched = re.sub(r'invoke-virtual(\/range)? (\{[^}]+\}), Landroid/hardware/camera2/CaptureRequest\$Builder;->set\(Landroid/hardware/camera2/CaptureRequest\$Key;Ljava/lang/Object;\)V',
                         r'invoke-static\1 \2, Llocal/sc51g/GalaxyCamera;->set(Landroid/hardware/camera2/CaptureRequest$Builder;Landroid/hardware/camera2/CaptureRequest$Key;Ljava/lang/Object;)V', source)
        patched = re.sub(r'invoke-virtual(\/range)? (\{[^}]+\}), Landroid/hardware/camera2/CaptureRequest;->get\(Landroid/hardware/camera2/CaptureRequest\$Key;\)Ljava/lang/Object;',
                         r'invoke-static\1 \2, Llocal/sc51g/GalaxyCamera;->get(Landroid/hardware/camera2/CaptureRequest;Landroid/hardware/camera2/CaptureRequest$Key;)Ljava/lang/Object;', patched)
        if patched != source:
            path.write_text(patched, encoding='utf-8')
    # The Sony sidecar JPEG processing device does not exist on Samsung.
    for method in ['openCamera()V', 'configSurface(Landroid/util/Size;)V']:
        replace_method('com/sonyericsson/android/camera/device/virtual/VirtualCameraDevice.smali', method, '    .locals 0\n    return-void')
    callback = DECODED / 'smali/com/sonyericsson/android/camera/device/CameraController$CaptureSessionCallback.smali'
    source = callback.read_text(encoding='utf-8')
    if 'Llocal/sc51g/GalaxyTelemetry;->onResult' not in source:
        signature = '.method public onCaptureCompleted(Landroid/hardware/camera2/CameraCaptureSession;Landroid/hardware/camera2/CaptureRequest;Landroid/hardware/camera2/TotalCaptureResult;)V'
        source, count = re.subn('(' + re.escape(signature) + r'\s+\.locals \d+)', r'\1\n    invoke-static {p3}, Llocal/sc51g/GalaxyTelemetry;->onResult(Landroid/hardware/camera2/TotalCaptureResult;)V', source)
        assert count == 1
        callback.write_text(source, encoding='utf-8')

    # Adapt the existing optical zoom preset from 2x to SC-51G's 3x telephoto.
    zoom_dir = DECODED / 'smali/com/sonyericsson/android/camera/view/baselayout/zoom'
    for path in zoom_dir.glob('ZoomDial*.smali'):
        source = path.read_text(encoding='utf-8')
        patched = source.replace('"x2"', '"x3"')
        patched = patched.replace('0x43cc0000    # 408.0f', '0x44094000    # 549.0f')
        # 549.0 cannot be encoded as const/high16; use the full 32-bit instruction.
        patched = re.sub(r'const/high16 ([vp]\d+), 0x44094000', r'const \1, 0x44094000', patched)
        patched = patched.replace('mZoomPoint2Step:I = 0x198', 'mZoomPoint2Step:I = 0x225')
        if path.name == 'ZoomDial.smali':
            # These two floats are the telephoto boundary, not view geometry.
            patched = patched.replace('const/high16 p1, 0x40000000    # 2.0f', 'const/high16 p1, 0x40400000    # 3.0f')
            patched = patched.replace('const/high16 v12, 0x40000000    # 2.0f', 'const/high16 v12, 0x40400000    # 3.0f')
        if patched != source:
            path.write_text(patched, encoding='utf-8')

    shortcut = 'com/sonyericsson/android/camera/view/PrimaryShortcutGroup.smali'
    def add_sound_button(method):
        if 'ShutterSoundControl;->addToList' in method:
            return method
        return method.replace('    return-object v0', '    invoke-static {p0, v0}, Llocal/sc51g/ShutterSoundControl;->addToList(Landroid/view/ViewGroup;Ljava/util/List;)V\n    return-object v0')
    edit_method(shortcut, 'getAllPrimaryShortcutView()Ljava/util/List;', add_sound_button)
    def add_color_button(method):
        if 'ColorSettings;->addToList' in method: return method
        return method.replace('    return-object v0','    invoke-static {p0, v0}, Llocal/sc51g/ColorSettings;->addToList(Landroid/view/ViewGroup;Ljava/util/List;)V\n    return-object v0')
    edit_method(shortcut, 'getAllPrimaryShortcutView()Ljava/util/List;', add_color_button)
    def hide_empty_settings(method):
        if ':sc51g_options_available' in method:
            return method
        return re.sub(r'(    \.locals \d+)', r'''\1
    iget-object v0, p0, Lcom/sonyericsson/android/camera/view/setting/settingitem/CameraSettingItemBuilder;->mStorage:Lcom/sonyericsson/cameracommon/storage/Storage;
    invoke-direct {p0, p3, p2, v0}, Lcom/sonyericsson/android/camera/view/setting/settingitem/CameraSettingItemBuilder;->generateChildrenSettingItem(Lcom/sonyericsson/android/camera/configuration/UserSettingKey;Lcom/sonyericsson/android/camera/setting/UserSettings;Lcom/sonyericsson/cameracommon/storage/Storage;)Ljava/util/List;
    move-result-object v0
    invoke-interface {v0}, Ljava/util/List;->isEmpty()Z
    move-result v0
    if-eqz v0, :sc51g_options_available
    const/4 v0, 0x0
    return v0
    :sc51g_options_available''', method, count=1)
    edit_method('com/sonyericsson/android/camera/view/setting/settingitem/CameraSettingItemBuilder.smali', 'isVisible(Landroid/content/Context;Lcom/sonyericsson/android/camera/setting/UserSettings;Lcom/sonyericsson/android/camera/configuration/UserSettingKey;)Z', hide_empty_settings)
    def rotate_sound_button(method):
        if 'ShutterSoundControl;->rotate' in method:
            return method
        return method.replace('    return-void', '''    invoke-static {p1}, Lcom/sonyericsson/cameracommon/utility/RotationUtil;->getAngle(I)F
    move-result v0
    invoke-static {p0, v0}, Llocal/sc51g/ShutterSoundControl;->rotate(Landroid/view/ViewGroup;F)V
    return-void''')
    edit_method(shortcut, 'setUiOrientation(I)V', rotate_sound_button)
    edit_method(shortcut, 'setUiOrientation(I)V', lambda method: method if 'ColorSettings;->rotate' in method else method.replace('    return-void', '''    invoke-static {p1}, Lcom/sonyericsson/cameracommon/utility/RotationUtil;->getAngle(I)F
    move-result v0
    invoke-static {p0, v0}, Llocal/sc51g/ColorSettings;->rotate(Landroid/view/ViewGroup;F)V
    return-void'''))
    def redirect_shutter(method):
        if 'ShutterSoundControl;->playShutter' in method:
            return method
        return re.sub(r'(    \.locals \d+)', r'''\1
    iget-object v0, p0, Lcom/sonyericsson/android/camera/device/CameraActionSound;->mApplicationContext:Landroid/content/Context;
    invoke-virtual {p1}, Lcom/sonyericsson/android/camera/device/CameraActionSound$Type;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Llocal/sc51g/ShutterSoundControl;->playShutter(Landroid/content/Context;Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :sc51g_original_sound
    return-void
    :sc51g_original_sound''', method, count=1)
    edit_method('com/sonyericsson/android/camera/device/CameraActionSound.smali', 'play(Lcom/sonyericsson/android/camera/device/CameraActionSound$Type;Z)V', redirect_shutter)
    replace_method('com/sonyericsson/android/camera/controller/StateMachine.smali', 'shouldPlayShutterSound()Z', '''
    .locals 1
    invoke-static {}, Lcom/sonyericsson/android/camera/CameraApplication;->getContext()Landroid/content/Context;
    move-result-object v0
    invoke-static {v0}, Llocal/sc51g/ShutterSoundControl;->isEnabled(Landroid/content/Context;)Z
    move-result v0
    return v0
''')
    replace_method('com/sonyericsson/android/camera/device/CameraDeviceHandler.smali', 'shouldPlayShutterSound(Lcom/sonyericsson/android/camera/controller/StateMachine;)Z', '''
    .locals 1
    invoke-virtual {p0}, Lcom/sonyericsson/android/camera/device/CameraDeviceHandler;->isRecording()Z
    move-result v0
    if-eqz v0, :check
    const/4 v0, 0x0
    return v0
    :check
    iget-object v0, p0, Lcom/sonyericsson/android/camera/device/CameraDeviceHandler;->mApplicationContext:Landroid/content/Context;
    invoke-static {v0}, Llocal/sc51g/ShutterSoundControl;->isEnabled(Landroid/content/Context;)Z
    move-result v0
    return v0
''')

if __name__ == '__main__':
    main()
