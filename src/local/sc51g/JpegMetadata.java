package local.sc51g;
import java.io.ByteArrayOutputStream;

/** Retain EXIF only: original compressed-image indexes and gain maps are stale after encoding. */
public final class JpegMetadata {
    public static byte[] preserveExif(byte[] original,byte[] encoded) {
        if (original.length<4 || encoded.length<4 || (original[0]&255)!=255 || (original[1]&255)!=216
                || (encoded[0]&255)!=255 || (encoded[1]&255)!=216) return encoded;
        ByteArrayOutputStream exif=new ByteArrayOutputStream();
        int position=2;
        while (position+4<=original.length && (original[position]&255)==255) {
            int marker=original[position+1]&255;
            if (marker==218 || marker==217) break;
            int length=((original[position+2]&255)<<8)|(original[position+3]&255);
            int end=position+2+length;
            if (length<2 || end>original.length) break;
            if (marker==225 && length>=8 && original[position+4]=='E' && original[position+5]=='x'
                    && original[position+6]=='i' && original[position+7]=='f'
                    && original[position+8]==0 && original[position+9]==0) {
                exif.write(original,position,end-position);
            }
            position=end;
        }
        if (exif.size()==0) return encoded;
        ByteArrayOutputStream output=new ByteArrayOutputStream(encoded.length+exif.size());
        output.write(encoded,0,2);
        byte[] segments=exif.toByteArray(); output.write(segments,0,segments.length);
        output.write(encoded,2,encoded.length-2);
        return output.toByteArray();
    }
}
