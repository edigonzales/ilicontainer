package ch.interlis.ilicontainer;

import static org.junit.Assert.*;

import ch.interlis.ilicontainer.api.*;
import ch.interlis.ilicontainer.codec.Cbor;
import ch.interlis.ilicontainer.container.*;
import ch.interlis.ilicontainer.index.*;
import ch.interlis.ilicontainer.remote.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import org.junit.*;
import org.junit.rules.TemporaryFolder;

public class IndexTest {
  @Rule public TemporaryFolder tmp = new TemporaryFolder();

  @Test
  public void externalMergeAndPagedLookup() throws Exception {
    Path dir = tmp.getRoot().toPath(), file = dir.resolve("tree.bin");
    long root;
    try (ExternalSort sort = new ExternalSort(dir, 16384);
        RandomAccessFile out = new RandomAccessFile(file.toFile(), "rw")) {
      Frames.header(out);
      for (int i = 9999; i >= 0; i--) sort.add("O\0" + FilesEx.number(i), Cbor.bytes(i));
      try (CloseableIterator<ExternalSort.Entry> entries = sort.finish()) {
        root = BTree.build(out, entries, dir);
      }
      Frames.footer(out, root, 0);
    }
    ReadMetrics metrics = new ReadMetrics();
    try (LocalSource source = new LocalSource(file, metrics)) {
      BTree tree = new BTree(new FrameStore(source, metrics, 32768), root);
      assertEquals(
          Integer.valueOf(1234), Cbor.read(tree.get("O\0" + FilesEx.number(1234)), Integer.class));
      assertTrue(metrics.indexPages < 10);
      assertNull(tree.get("missing"));
      int count = 0;
      try (CloseableIterator<ExternalSort.Entry> all = tree.range("O\0")) {
        while (all.hasNext()) {
          all.next();
          count++;
        }
      }
      assertEquals(10000, count);
    }
  }

  @Test
  public void oversizedIndexFieldsUseOverflowFrames() throws Exception {
    Path dir = tmp.getRoot().toPath(), file = dir.resolve("overflow.bin");
    long root;
    String key = String.join("", Collections.nCopies(20000, "x"));
    byte[] value = new byte[50000];
    Arrays.fill(value, (byte) 7);
    try (ExternalSort sort = new ExternalSort(dir, 16384);
        RandomAccessFile out = new RandomAccessFile(file.toFile(), "rw")) {
      Frames.header(out);
      sort.add(key, value);
      try (CloseableIterator<ExternalSort.Entry> entries = sort.finish()) {
        root = BTree.build(out, entries, dir);
      }
      Frames.footer(out, root, 0);
    }
    ReadMetrics metrics = new ReadMetrics();
    try (LocalSource source = new LocalSource(file, metrics)) {
      BTree tree = new BTree(new FrameStore(source, metrics, 1024), root);
      assertArrayEquals(value, tree.get(key));
    }
  }

  @Test
  public void cyclicBranchReferenceFailsDespiteValidChecksum() throws Exception {
    Path file = tmp.getRoot().toPath().resolve("invalid.bin");
    long root = Frames.HEADER_SIZE;
    ByteArrayOutputStream bytes = new ByteArrayOutputStream();
    DataOutputStream payload = new DataOutputStream(bytes);
    payload.writeInt(1);
    payload.writeInt(1);
    payload.writeByte('a');
    payload.writeInt(8);
    payload.writeLong(root);
    try (RandomAccessFile out = new RandomAccessFile(file.toFile(), "rw")) {
      Frames.header(out);
      Frames.write(out, Frames.BRANCH, bytes.toByteArray());
      Frames.footer(out, root, 0);
    }
    ReadMetrics metrics = new ReadMetrics();
    try (LocalSource source = new LocalSource(file, metrics)) {
      BTree tree = new BTree(new FrameStore(source, metrics, 1024), root);
      try {
        tree.get("a");
        fail("cyclic index accepted");
      } catch (IOException expected) {
        assertTrue(expected.getMessage().contains("reference"));
      }
    }
  }
}
