package ch.interlis.ilicontainer.remote;

import ch.interlis.ilicontainer.api.ReadMetrics;
import java.io.*;
import java.nio.file.Path;

public final class LocalSource implements RangeSource {
  private final RandomAccessFile file;
  private final ReadMetrics metrics;

  public LocalSource(Path path, ReadMetrics metrics) throws IOException {
    file = new RandomAccessFile(path.toFile(), "r");
    this.metrics = metrics;
  }

  public long size() throws IOException {
    return file.length();
  }

  public synchronized byte[] read(long offset, int length) throws IOException {
    if (offset < 0 || length < 0 || offset > size() - length)
      throw new EOFException("Range outside container");
    byte[] data = new byte[length];
    file.seek(offset);
    file.readFully(data);
    metrics.bytesRead += length;
    return data;
  }

  public void close() throws IOException {
    file.close();
  }
}
