package ch.interlis.ilicontainer.container;

import ch.interlis.ilicontainer.remote.RangeSource;
import java.io.*;
import java.nio.ByteBuffer;
import java.util.zip.CRC32;

public final class Frames {
  public static final long MAGIC = 0x494c49434f4e5431L, FOOTER_MAGIC = 0x494c4943464f4f31L;
  public static final int VERSION = 1, HEADER_SIZE = 16, FRAME_HEADER = 16, FOOTER_SIZE = 40;
  public static final int METADATA = 1,
      BASKET = 2,
      CHUNK = 3,
      END_BASKET = 4,
      END_TRANSFER = 5,
      LEAF = 6,
      BRANCH = 7,
      SPATIAL_LEAF = 8,
      SPATIAL_BRANCH = 9,
      SPATIAL_MANIFEST = 10,
      OVERFLOW = 11;

  private Frames() {}

  public static int crc(byte[] data) {
    CRC32 c = new CRC32();
    c.update(data);
    return (int) c.getValue();
  }

  public static void header(DataOutput out) throws IOException {
    header(out, VERSION);
  }

  public static void header(DataOutput out, int version) throws IOException {
    out.writeLong(MAGIC);
    out.writeInt(version);
    out.writeInt(0);
  }

  public static int checkHeader(DataInput in) throws IOException {
    long magic = in.readLong();
    int version = in.readInt();
    int features = in.readInt();
    if (magic != MAGIC || (version != 1 && version != 2) || features != 0)
      throw new IOException("Unsupported IliContainer header/version/features");
    return version;
  }

  public static long write(RandomAccessFile out, int type, byte[] data) throws IOException {
    long offset = out.getFilePointer();
    out.writeInt(type);
    out.writeLong(data.length);
    out.writeInt(crc(data));
    out.write(data);
    return offset;
  }

  public static final class Frame {
    public int type;
    public byte[] data;
    public long end;
  }

  public static Frame read(RangeSource source, long offset) throws IOException {
    if (offset < HEADER_SIZE || offset > source.size() - FRAME_HEADER)
      throw new IOException("Invalid frame offset " + offset);
    byte[] header = source.read(offset, FRAME_HEADER);
    ByteBuffer h = ByteBuffer.wrap(header);
    Frame f = new Frame();
    f.type = h.getInt();
    long length = h.getLong();
    int checksum = h.getInt();
    if (length < 0
        || length > Integer.MAX_VALUE - 32
        || length > source.size() - offset - FRAME_HEADER)
      throw new IOException("Invalid frame length");
    f.data = source.read(offset + FRAME_HEADER, (int) length);
    f.end = offset + FRAME_HEADER + length;
    if (crc(f.data) != checksum) throw new IOException("Frame checksum mismatch at " + offset);
    return f;
  }

  public static Frame read(DataInputStream in) throws IOException {
    Frame f = new Frame();
    f.type = in.readInt();
    long length = in.readLong();
    int checksum = in.readInt();
    if (length < 0 || length > Integer.MAX_VALUE - 32)
      throw new IOException("Invalid frame length");
    f.data = new byte[(int) length];
    in.readFully(f.data);
    if (crc(f.data) != checksum) throw new IOException("Frame checksum mismatch");
    return f;
  }

  public static void footer(RandomAccessFile out, long root, long spatial) throws IOException {
    long position = out.getFilePointer();
    out.seek(8);
    int version = out.readInt();
    out.seek(position);
    long size = position + FOOTER_SIZE;
    ByteBuffer b = ByteBuffer.allocate(32);
    b.putLong(FOOTER_MAGIC).putLong(root).putLong(spatial).putLong(size);
    out.write(b.array());
    out.writeInt(crc(b.array()));
    out.writeInt(version);
  }

  public static long[] footer(RangeSource source) throws IOException {
    long size = source.size();
    if (size < HEADER_SIZE + FOOTER_SIZE) throw new IOException("Truncated container");
    byte[] bytes = source.read(size - FOOTER_SIZE, FOOTER_SIZE);
    ByteBuffer b = ByteBuffer.wrap(bytes);
    long magic = b.getLong(), root = b.getLong(), spatial = b.getLong(), storedSize = b.getLong();
    int crc = b.getInt(), version = b.getInt();
    if (magic != FOOTER_MAGIC
        || storedSize != size
        || (version != 1 && version != 2)
        || crc != crc(java.util.Arrays.copyOf(bytes, 32)))
      throw new IOException("Invalid/truncated footer");
    if (root < HEADER_SIZE
        || root >= size - FOOTER_SIZE
        || spatial < 0
        || spatial >= size - FOOTER_SIZE) throw new IOException("Invalid footer pointers");
    int headerVersion =
        checkHeader(new DataInputStream(new ByteArrayInputStream(source.read(0, HEADER_SIZE))));
    if (version != headerVersion) throw new IOException("Header/footer version mismatch");
    return new long[] {root, spatial};
  }
}
