package ch.interlis.ilicontainer.index;

import ch.interlis.ilicontainer.container.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.file.*;
import java.util.*;

/** Immutable B+ tree; leaves and branch levels are built from sequential disk streams. */
public final class BTree {
  private static final int PAGE = 16 * 1024;
  private final FrameStore store;
  private final long root;

  public BTree(FrameStore store, long root) {
    this.store = store;
    this.root = root;
  }

  public static long build(
      RandomAccessFile out, CloseableIterator<ExternalSort.Entry> sorted, Path tmp)
      throws IOException {
    Path current = Files.createTempFile(tmp, "level-", ".run");
    long count = 0;
    String previous = null;
    try (DataOutputStream refs =
        new DataOutputStream(new BufferedOutputStream(Files.newOutputStream(current)))) {
      List<ExternalSort.Entry> page = new ArrayList<ExternalSort.Entry>();
      int bytes = 0;
      while (sorted.hasNext()) {
        ExternalSort.Entry e = sorted.next();
        if (e.key.equals(previous))
          throw new IOException("Duplicate identity/index key: " + e.key.replace('\0', '/'));
        previous = e.key;
        if (bytes >= PAGE && !page.isEmpty()) {
          ref(refs, out, page, true);
          count++;
          page.clear();
          bytes = 0;
        }
        page.add(e);
        bytes += e.key.length() * 3 + e.value.length + 8;
      }
      if (!page.isEmpty() || count == 0) {
        ref(refs, out, page, true);
        count++;
      }
    }
    while (count > 1) {
      Path next = Files.createTempFile(tmp, "level-", ".run");
      long n = 0;
      try (DataInputStream in =
              new DataInputStream(new BufferedInputStream(Files.newInputStream(current)));
          DataOutputStream refs =
              new DataOutputStream(new BufferedOutputStream(Files.newOutputStream(next)))) {
        List<ExternalSort.Entry> page = new ArrayList<ExternalSort.Entry>();
        int bytes = 0;
        ExternalSort.Entry e;
        while ((e = ExternalSort.read(in)) != null) {
          if (bytes >= PAGE && page.size() >= 2) {
            ref(refs, out, page, false);
            n++;
            page.clear();
            bytes = 0;
          }
          page.add(e);
          bytes += e.key.length() * 3 + 16;
        }
        if (!page.isEmpty()) {
          ref(refs, out, page, false);
          n++;
        }
      }
      Files.delete(current);
      current = next;
      count = n;
    }
    try (DataInputStream in = new DataInputStream(Files.newInputStream(current))) {
      return ByteBuffer.wrap(ExternalSort.read(in).value).getLong();
    } finally {
      Files.delete(current);
    }
  }

  private static void ref(
      DataOutputStream refs, RandomAccessFile out, List<ExternalSort.Entry> entries, boolean leaf)
      throws IOException {
    ByteArrayOutputStream bytes = new ByteArrayOutputStream();
    DataOutputStream data = new DataOutputStream(bytes);
    data.writeInt(entries.size());
    for (ExternalSort.Entry e : entries) {
      writeField(data, out, e.key.getBytes("UTF-8"));
      writeField(data, out, e.value);
    }
    long offset = Frames.write(out, leaf ? Frames.LEAF : Frames.BRANCH, bytes.toByteArray());
    ExternalSort.write(
        refs,
        new ExternalSort.Entry(
            entries.isEmpty() ? "" : entries.get(0).key,
            ByteBuffer.allocate(8).putLong(offset).array()));
  }

  private static void writeField(DataOutputStream data, RandomAccessFile out, byte[] value)
      throws IOException {
    if (value.length > PAGE / 2) {
      data.writeInt(-1);
      data.writeLong(Frames.write(out, Frames.OVERFLOW, value));
    } else {
      data.writeInt(value.length);
      data.write(value);
    }
  }

  private byte[] readField(DataInputStream in) throws IOException {
    int size = in.readInt();
    if (size == -1) {
      long offset = in.readLong();
      Frames.Frame f = store.read(offset);
      if (f.type != Frames.OVERFLOW) throw new IOException("Invalid overflow reference");
      return f.data;
    }
    if (size < 0 || size > in.available()) throw new IOException("Invalid index field length");
    byte[] b = new byte[size];
    in.readFully(b);
    return b;
  }

  private List<ExternalSort.Entry> entries(Frames.Frame frame) throws IOException {
    if (frame.type != Frames.LEAF && frame.type != Frames.BRANCH)
      throw new IOException("Invalid B-tree page type");
    DataInputStream in = new DataInputStream(new ByteArrayInputStream(frame.data));
    int n = in.readInt();
    if (n < 0 || n > frame.data.length / 8) throw new IOException("Invalid B-tree page count");
    List<ExternalSort.Entry> list = new ArrayList<ExternalSort.Entry>();
    String prev = null;
    for (int i = 0; i < n; i++) {
      ExternalSort.Entry e =
          new ExternalSort.Entry(new String(readField(in), "UTF-8"), readField(in));
      if ((prev != null && prev.compareTo(e.key) >= 0))
        throw new IOException("Invalid B-tree ordering");
      list.add(e);
      prev = e.key;
    }
    if (in.available() != 0) throw new IOException("Trailing index bytes");
    return list;
  }

  public byte[] get(String key) throws IOException {
    try (CloseableIterator<ExternalSort.Entry> it = range(key)) {
      if (it.hasNext()) {
        ExternalSort.Entry e = it.next();
        if (e.key.equals(key)) return e.value;
      }
      return null;
    }
  }

  public CloseableIterator<ExternalSort.Entry> range(String prefix) throws IOException {
    return new Cursor(prefix);
  }

  private final class Cursor implements CloseableIterator<ExternalSort.Entry> {
    final String prefix;
    final Deque<Level> stack = new ArrayDeque<Level>();
    ExternalSort.Entry next;

    final class Level {
      List<ExternalSort.Entry> entries;
      int i;
      boolean leaf;
      long offset;

      Level(List<ExternalSort.Entry> e, int i, boolean l, long offset) {
        entries = e;
        this.i = i;
        leaf = l;
        this.offset = offset;
      }
    }

    Cursor(String prefix) throws IOException {
      this.prefix = prefix;
      descend(root, true, 0);
      advance();
    }

    void descend(long offset, boolean seek, int depth) throws IOException {
      if (depth + stack.size() > 64) throw new IOException("B-tree cycle/excessive depth");
      Frames.Frame f = store.read(offset);
      List<ExternalSort.Entry> es = entries(f);
      int i = 0;
      if (f.type == Frames.LEAF) {
        if (seek) while (i < es.size() && es.get(i).key.compareTo(prefix) < 0) i++;
        stack.push(new Level(es, i, true, offset));
      } else {
        if (es.isEmpty()) throw new IOException("Empty branch");
        if (seek) while (i + 1 < es.size() && es.get(i + 1).key.compareTo(prefix) <= 0) i++;
        stack.push(new Level(es, i + 1, false, offset));
        long child = pointer(es.get(i), offset);
        descend(child, seek, depth + 1);
      }
    }

    long pointer(ExternalSort.Entry e, long parent) throws IOException {
      if (e.value.length != 8) throw new IOException("Invalid branch reference");
      long offset = ByteBuffer.wrap(e.value).getLong();
      if (offset >= parent || offset < Frames.HEADER_SIZE)
        throw new IOException("Invalid/cyclic branch reference");
      return offset;
    }

    void advance() throws IOException {
      next = null;
      while (!stack.isEmpty()) {
        Level l = stack.peek();
        if (l.i >= l.entries.size()) {
          stack.pop();
          continue;
        }
        ExternalSort.Entry e = l.entries.get(l.i++);
        if (l.leaf) {
          if (e.key.startsWith(prefix)) {
            next = e;
            return;
          }
          stack.clear();
          return;
        }
        long ptr = pointer(e, l.offset);
        descend(ptr, false, 0);
      }
    }

    public boolean hasNext() {
      return next != null;
    }

    public ExternalSort.Entry next() {
      if (next == null) throw new NoSuchElementException();
      ExternalSort.Entry result = next;
      try {
        advance();
      } catch (IOException e) {
        throw new UncheckedIOException(e);
      }
      return result;
    }

    public void close() {
      stack.clear();
      next = null;
    }
  }
}
