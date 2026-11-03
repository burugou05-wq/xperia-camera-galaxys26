import local.sc51g.ColorMath;
import local.sc51g.JpegMetadata;
import java.util.Arrays;
import java.util.Random;

public final class ColorMathCheck {
    static void check(boolean condition,String label){if(!condition)throw new AssertionError(label);}
    public static void main(String[] args){
        Random random=new Random(17);
        for(int i=0;i<100000;i++){
            int pixel=random.nextInt();
            check(ColorMath.apply(pixel,0)==pixel,"zero strength must preserve pixel exactly");
            int output=ColorMath.apply(pixel,1);
            check((output&0xff000000)==(pixel&0xff000000),"alpha must survive");
        }
        check(ColorMath.apply(0xff000000,1)==0xff000000,"black anchor");
        check(ColorMath.safeGain(-.3f)==.1f && ColorMath.safeGain(25)==8f,"gain safety bounds");
        byte[] original={(byte)255,(byte)216,(byte)255,(byte)225,0,10,'E','x','i','f',0,0,12,34,(byte)255,(byte)218,0,2};
        byte[] encoded={(byte)255,(byte)216,(byte)255,(byte)224,0,2,(byte)255,(byte)217};
        byte[] combined=JpegMetadata.preserveExif(original,encoded);
        check(combined.length==encoded.length+12,"EXIF segment size");
        check(combined[3]==(byte)225 && combined[6]=='E' && combined[12]==12,"original EXIF payload");
        check(Arrays.equals(JpegMetadata.preserveExif(new byte[]{1,2},encoded),encoded),"invalid input safe fallback");
        check(Arrays.equals(JpegMetadata.preserveExif(encoded,encoded),encoded),"no EXIF leaves encoded data unchanged");
        System.out.println("100000 pixel identity/alpha checks, black anchor, gain bounds and EXIF preservation passed.");
    }
}
