package local.sc51g;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.ColorSpace;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CaptureRequest;
import android.hardware.camera2.CaptureResult;
import android.hardware.camera2.TotalCaptureResult;
import android.hardware.camera2.params.ColorSpaceTransform;
import android.hardware.camera2.params.RggbChannelVector;
import android.os.SystemClock;
import android.util.Log;
import java.io.ByteArrayOutputStream;

/** Standard Camera2 translation of the supplied APK's gain formula, plus opt-in JPEG transfer. */
public final class ColorPipeline {
    private static Context application;
    private static volatile RggbChannelVector requestedGains;
    private static volatile ColorSpaceTransform autoTransform;
    private static volatile RggbChannelVector autoGains;
    private static long lastLog;
    public static void initialize(Context context) { application=context.getApplicationContext(); }
    public static synchronized void reset() { requestedGains=null; autoTransform=null; autoGains=null; }
    public static int warmthLimit(CameraCharacteristics characteristics) {
        int[] modes=characteristics.get(CameraCharacteristics.CONTROL_AWB_AVAILABLE_MODES);
        int[] caps=characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES);
        boolean off=false,manual=false;
        if (modes!=null) for (int mode:modes) if (mode==CaptureRequest.CONTROL_AWB_MODE_OFF) off=true;
        if (caps!=null) for (int cap:caps) if (cap==CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_MANUAL_POST_PROCESSING) manual=true;
        return off&&manual ? 7:0;
    }
    public static synchronized void requestWarmth(int value,RggbChannelVector formulaResult) {
        requestedGains=value==-100 || value==0 ? null:formulaResult;
        Log.i("SC51GColor","warmth step="+value+" enabled="+(requestedGains!=null));
    }
    public static void observe(TotalCaptureResult result) {
        Integer mode=result.get(CaptureResult.CONTROL_AWB_MODE);
        if (mode!=null && mode==CaptureRequest.CONTROL_AWB_MODE_AUTO) {
            RggbChannelVector gains=result.get(CaptureResult.COLOR_CORRECTION_GAINS);
            ColorSpaceTransform transform=result.get(CaptureResult.COLOR_CORRECTION_TRANSFORM);
            if (gains!=null && transform!=null) { autoGains=gains; autoTransform=transform; }
        }
        long now=SystemClock.uptimeMillis();
        if (now-lastLog>=2000) {
            lastLog=now;
            Log.i("SC51GColor","result awb="+mode+" gains="+result.get(CaptureResult.COLOR_CORRECTION_GAINS));
        }
    }
    public static void prepare(CaptureRequest.Builder builder) {
        RggbChannelVector gains=requestedGains;
        ColorSpaceTransform transform=autoTransform;
        if (gains==null || transform==null) return;
        Integer awb=builder.get(CaptureRequest.CONTROL_AWB_MODE);
        if (awb!=null && awb!=CaptureRequest.CONTROL_AWB_MODE_AUTO && awb!=CaptureRequest.CONTROL_AWB_MODE_OFF) return;
        try {
            builder.set(CaptureRequest.CONTROL_AWB_MODE,CaptureRequest.CONTROL_AWB_MODE_OFF);
            builder.set(CaptureRequest.COLOR_CORRECTION_MODE,CaptureRequest.COLOR_CORRECTION_MODE_TRANSFORM_MATRIX);
            builder.set(CaptureRequest.COLOR_CORRECTION_TRANSFORM,transform);
            builder.set(CaptureRequest.COLOR_CORRECTION_GAINS,new RggbChannelVector(
                    ColorMath.safeGain(gains.getRed()),ColorMath.safeGain(gains.getGreenEven()),
                    ColorMath.safeGain(gains.getGreenOdd()),ColorMath.safeGain(gains.getBlue())));
        } catch (IllegalArgumentException failure) {
            builder.set(CaptureRequest.CONTROL_AWB_MODE,CaptureRequest.CONTROL_AWB_MODE_AUTO);
            builder.set(CaptureRequest.COLOR_CORRECTION_MODE,CaptureRequest.COLOR_CORRECTION_MODE_FAST);
            builder.set(CaptureRequest.COLOR_CORRECTION_TRANSFORM,null);
            builder.set(CaptureRequest.COLOR_CORRECTION_GAINS,null);
            Log.w("SC51GColor","manual color rejected; restored auto",failure);
        }
    }
    public static byte[] processJpeg(byte[] original) {
        Context context=application;
        if (context==null || !ColorSettings.enabled(context)) return original;
        float strength=ColorSettings.strength(context)/100f;
        if (strength<=0) return original;
        long started=SystemClock.uptimeMillis();
        Bitmap bitmap=null;
        try {
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inMutable=true; options.inPreferredConfig=Bitmap.Config.ARGB_8888;
            options.inPreferredColorSpace=ColorSpace.get(ColorSpace.Named.SRGB);
            bitmap=BitmapFactory.decodeByteArray(original,0,original.length,options);
            if (bitmap==null) return original;
            int width=bitmap.getWidth(),height=bitmap.getHeight();
            int[] row=new int[width];
            for (int y=0;y<height;y++) {
                bitmap.getPixels(row,0,width,0,y,width,1);
                for (int x=0;x<width;x++) row[x]=ColorMath.apply(row[x],strength);
                bitmap.setPixels(row,0,width,0,y,width,1);
            }
            ByteArrayOutputStream buffer=new ByteArrayOutputStream(original.length);
            if (!bitmap.compress(Bitmap.CompressFormat.JPEG,97,buffer)) return original;
            byte[] output=JpegMetadata.preserveExif(original,buffer.toByteArray());
            Log.i("SC51GColor","JPEG web-reference strength="+strength+" size="+width+"x"+height+" ms="+(SystemClock.uptimeMillis()-started));
            return output;
        } catch (RuntimeException|OutOfMemoryError failure) {
            Log.w("SC51GColor","color processing failed; preserving original JPEG",failure);
            return original;
        } finally { if (bitmap!=null) bitmap.recycle(); }
    }
}
