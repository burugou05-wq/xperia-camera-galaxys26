package local.sc51g;

/** Pure numerical operations shared by the Android pipeline and host checks. */
public final class ColorMath {
    private static final float[] LINEAR = new float[256];
    private static final int[] SRGB = new int[65536];
    static {
        for (int i=0;i<256;i++) {
            double x=i/255.0;
            LINEAR[i]=(float)(x<=.04045 ? x/12.92 : Math.pow((x+.055)/1.055,2.4));
        }
        for (int i=0;i<SRGB.length;i++) {
            double x=i/65535.0;
            SRGB[i]=(int)Math.round(255*(x<=.0031308 ? 12.92*x : 1.055*Math.pow(x,1/2.4)-.055));
        }
    }
    public static float safeGain(float value) { return Math.max(.1f, Math.min(8f,value)); }
    private static int encode(float value) { return SRGB[Math.max(0,Math.min(65535,Math.round(value*65535)))]; }
    public static int apply(int pixel,float strength) {
        if (strength<=0) return pixel;
        strength=Math.min(1,strength);
        float r=LINEAR[(pixel>>16)&255],g=LINEAR[(pixel>>8)&255],b=LINEAR[pixel&255];
        float[] m=ColorReference.MATRIX;
        int red=encode(r+strength*(m[0]*r+m[1]*g+m[2]*b-r));
        int green=encode(g+strength*(m[3]*r+m[4]*g+m[5]*b-g));
        int blue=encode(b+strength*(m[6]*r+m[7]*g+m[8]*b-b));
        return (pixel&0xff000000)|(red<<16)|(green<<8)|blue;
    }
}
