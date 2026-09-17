package ch.interlis.ilicontainer.spatial;

import ch.interlis.ilicontainer.api.*;
import ch.interlis.ilicontainer.codec.Cbor;
import ch.interlis.ilicontainer.container.*;
import ch.interlis.ilicontainer.index.ExternalSort;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Packed immutable R-tree; leaves carry physical object locations. */
public final class SpatialIndex {
  public static final class Manifest {
    public Map<String, Info> indexes = new TreeMap<String, Info>();
  }

  public static final class Info {
    public String className, attribute, crs, axes = "C1,C2";
    public long root, count;
  }

  public static final class Entry {
    public BoundingBox box;
    public Location location;
    public long child;
  }

  public static final class Node {
    public List<Entry> entries = new ArrayList<Entry>();
  }

  private static String key(String cls, String attr) {
    return cls + "\0" + attr;
  }

  public static Manifest manifest(IliContainer c) throws IOException {
    if (c.spatialRoot() == 0) return new Manifest();
    Frames.Frame f = c.frameStore().read(c.spatialRoot());
    if (f.type != Frames.SPATIAL_MANIFEST) throw new IOException("Invalid spatial manifest");
    return Cbor.read(f.data, Manifest.class);
  }

  public static void add(Path path, String cls, String attr, String explicitCrs) throws Exception {
    Path parent = path.toAbsolutePath().getParent(),
        temp = Files.createTempDirectory(parent, ".ilic-spatial-"),
        output = Files.createTempFile(parent, ".ilic-spatial-", ".tmp");
    try {
      try (IliContainer c = IliContainer.open(path);
          ExternalSort entries = new ExternalSort(temp, 16L * 1024 * 1024)) {
        if (!c.metadata().classes.containsKey(cls))
          throw new IOException("Unknown spatial class " + cls);
        String known = c.metadata().geometryCrs.get(cls + "." + attr);
        if (known == null) throw new IOException("Unknown geometry attribute " + cls + "." + attr);
        String crs = explicitCrs != null ? explicitCrs : known;
        if (crs == null || crs.trim().isEmpty())
          throw new IOException("An unambiguous CRS is required; supply --crs");
        if (explicitCrs != null
            && !known.isEmpty()
            && !normalize(known).equals(normalize(explicitCrs)))
          throw new IOException("Explicit CRS conflicts with model CRS");
        long count = 0;
        String domainSignature = null;
        try (Fragment fragment = c.getClass(cls);
            CloseableIterator<Location> refs = fragment.locations()) {
          while (refs.hasNext()) {
            Location loc = refs.next();
            if (loc.chunkOffset == 0) continue;
            BasketContext basket = c.basket(loc);
            if (!basket.domains.isEmpty()
                && explicitCrs == null
                && !"wkb".equals(c.metadata().geometryEncoding))
              throw new IOException(
                  "Basket generic-domain assignments require an explicit verified CRS");
            String signature = new TreeMap<String, String>(basket.domains).toString();
            if (domainSignature == null) domainSignature = signature;
            else if (!domainSignature.equals(signature))
              throw new IOException(
                  "Mixed basket coordinate-domain assignments cannot share an index");
            try (ObjectCursor objects = c.objects(loc)) {
              int ordinal = 0;
              while (objects.hasNext()) {
                BoundingBox box;
                if ("wkb".equals(c.metadata().geometryEncoding))
                  box =
                      new ch.interlis.ilicontainer.codec.ObjectCodec(c.metadata(), true)
                          .geometryBounds(objects.nextRecord(), attr);
                else box = GeometryBounds.attribute(objects.next(), attr);
                if (box != null) {
                  Entry e = new Entry();
                  e.box = box;
                  e.location =
                      new Location(
                          loc.chunkOffset,
                          loc.basketOffset,
                          loc.basketPosition,
                          loc.chunkId,
                          ordinal);
                  entries.add(sortKey(box.minX) + FilesEx.number(count), Cbor.bytes(e));
                  count++;
                }
                ordinal++;
              }
            }
          }
        }
        Files.copy(path, output, StandardCopyOption.REPLACE_EXISTING);
        try (RandomAccessFile out = new RandomAccessFile(output.toFile(), "rw")) {
          out.setLength(out.length() - Frames.FOOTER_SIZE);
          out.seek(out.length());
          long root;
          try (CloseableIterator<ExternalSort.Entry> sorted = entries.finish()) {
            root = build(out, sorted, temp);
          }
          Manifest manifest = manifest(c);
          Info info = new Info();
          info.className = cls;
          info.attribute = attr;
          info.crs = crs;
          info.root = root;
          info.count = count;
          manifest.indexes.put(key(cls, attr), info);
          long manifestOffset = Frames.write(out, Frames.SPATIAL_MANIFEST, Cbor.bytes(manifest));
          Frames.footer(out, c.indexRoot(), manifestOffset);
          out.getFD().sync();
        }
      }
      FilesEx.publish(output, path.toAbsolutePath(), true);
    } finally {
      Files.deleteIfExists(output);
      FilesEx.deleteTree(temp);
    }
  }

  private static String normalize(String s) {
    return s.toUpperCase(Locale.ROOT).replace(" ", "");
  }

  private static String sortKey(double value) {
    long bits = Double.doubleToLongBits(value);
    bits = bits < 0 ? ~bits : bits ^ Long.MIN_VALUE;
    return String.format(Locale.ROOT, "%016x", bits);
  }

  private static Entry writeNode(RandomAccessFile out, Node node, boolean leaf) throws IOException {
    long offset =
        Frames.write(out, leaf ? Frames.SPATIAL_LEAF : Frames.SPATIAL_BRANCH, Cbor.bytes(node));
    Entry ref = new Entry();
    ref.child = offset;
    for (Entry e : node.entries) {
      if (ref.box == null)
        ref.box = new BoundingBox(e.box.minX, e.box.minY, e.box.maxX, e.box.maxY);
      else ref.box.expand(e.box);
    }
    return ref;
  }

  private static long build(
      RandomAccessFile out, CloseableIterator<ExternalSort.Entry> sorted, Path temp)
      throws IOException {
    Path current = Files.createTempFile(temp, "spatial-level-", ".run");
    long count = 0;
    try (DataOutputStream refs =
        new DataOutputStream(new BufferedOutputStream(Files.newOutputStream(current)))) {
      Node n = new Node();
      while (sorted.hasNext()) {
        n.entries.add(Cbor.read(sorted.next().value, Entry.class));
        if (n.entries.size() == 64) {
          ExternalSort.write(refs, new ExternalSort.Entry("", Cbor.bytes(writeNode(out, n, true))));
          count++;
          n = new Node();
        }
      }
      if (!n.entries.isEmpty() || count == 0) {
        ExternalSort.write(refs, new ExternalSort.Entry("", Cbor.bytes(writeNode(out, n, true))));
        count++;
      }
    }
    while (count > 1) {
      Path next = Files.createTempFile(temp, "spatial-level-", ".run");
      long ncount = 0;
      try (DataInputStream in =
              new DataInputStream(new BufferedInputStream(Files.newInputStream(current)));
          DataOutputStream refs =
              new DataOutputStream(new BufferedOutputStream(Files.newOutputStream(next)))) {
        Node n = new Node();
        ExternalSort.Entry e;
        while ((e = ExternalSort.read(in)) != null) {
          n.entries.add(Cbor.read(e.value, Entry.class));
          if (n.entries.size() == 64) {
            ExternalSort.write(
                refs, new ExternalSort.Entry("", Cbor.bytes(writeNode(out, n, false))));
            ncount++;
            n = new Node();
          }
        }
        if (!n.entries.isEmpty()) {
          ExternalSort.write(
              refs, new ExternalSort.Entry("", Cbor.bytes(writeNode(out, n, false))));
          ncount++;
        }
      }
      Files.delete(current);
      current = next;
      count = ncount;
    }
    try (DataInputStream in = new DataInputStream(Files.newInputStream(current))) {
      return Cbor.read(ExternalSort.read(in).value, Entry.class).child;
    } finally {
      Files.delete(current);
    }
  }

  public static Fragment query(IliContainer c, String cls, String attr, BoundingBox box)
      throws IOException {
    Info info = manifest(c).indexes.get(key(cls, attr));
    if (info == null) throw new IOException("No spatial index for " + cls + "." + attr);
    return new Fragment(
        c,
        () -> candidates(c, info, box),
        "bbox candidates "
            + cls
            + "."
            + attr
            + " ["
            + box.minX
            + ","
            + box.minY
            + ","
            + box.maxX
            + ","
            + box.maxY
            + "] "
            + info.crs);
  }

  private static CloseableIterator<Location> candidates(IliContainer c, Info info, BoundingBox box)
      throws IOException {
    Path temp = Files.createTempDirectory("ilic-candidates-");
    ExternalSort sorted = new ExternalSort(temp, 4L * 1024 * 1024);
    try {
      visit(c, info.root, box, sorted, 0);
      final CloseableIterator<ExternalSort.Entry> it = sorted.finish();
      return new CloseableIterator<Location>() {
        public boolean hasNext() {
          return it.hasNext();
        }

        public Location next() {
          try {
            return Cbor.read(it.next().value, Location.class);
          } catch (IOException e) {
            throw new UncheckedIOException(e);
          }
        }

        public void close() throws IOException {
          try {
            it.close();
            sorted.close();
          } finally {
            FilesEx.deleteTree(temp);
          }
        }
      };
    } catch (IOException | RuntimeException e) {
      sorted.close();
      FilesEx.deleteTree(temp);
      throw e;
    }
  }

  private static void visit(
      IliContainer c, long offset, BoundingBox box, ExternalSort sorted, int depth)
      throws IOException {
    if (depth > 64) throw new IOException("Spatial tree excessive depth");
    Frames.Frame f = c.frameStore().read(offset);
    if (f.type != Frames.SPATIAL_LEAF && f.type != Frames.SPATIAL_BRANCH)
      throw new IOException("Invalid spatial node");
    Node n = Cbor.read(f.data, Node.class);
    for (Entry e : n.entries) {
      if (e.box == null) throw new IOException("Missing spatial bounds");
      if (!e.box.intersects(box)) continue;
      if (f.type == Frames.SPATIAL_LEAF) {
        if (e.location == null || e.location.ordinal < 0)
          throw new IOException("Invalid spatial location");
        Location loc = e.location;
        sorted.add(
            FilesEx.number(loc.basketPosition)
                + FilesEx.number(loc.chunkId)
                + FilesEx.number(loc.ordinal),
            Cbor.bytes(loc));
      } else {
        if (e.child < Frames.HEADER_SIZE || e.child >= offset)
          throw new IOException("Invalid/cyclic spatial pointer");
        visit(c, e.child, box, sorted, depth + 1);
      }
    }
  }
}
