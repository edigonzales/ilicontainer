package ch.interlis.ilicontainer.remote;

import java.io.*;

public interface RangeSource extends Closeable {
  long size() throws IOException;

  byte[] read(long offset, int length) throws IOException;
}
