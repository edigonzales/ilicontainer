package ch.interlis.ilicontainer.api;

import ch.interlis.ilicontainer.codec.*;
import ch.interlis.ilicontainer.container.*;
import ch.interlis.ilicontainer.index.*;
import ch.interlis.ilicontainer.iox.ModelBridge;
import ch.interlis.ilicontainer.remote.*;
import ch.interlis.iom_j.xtf.XtfWriterBase;
import ch.interlis.iox.*;
import java.io.*;
import java.net.URI;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Stream;

public final class IliContainer implements AutoCloseable {
  private final RangeSource source;
  private final FrameStore store;
  private final TransferMetadata metadata;
  private final ObjectCodec codec;
  private final BTree tree;
  private final long[] roots;
  private final ReadMetrics metrics;
  private boolean closed;

  public static IliContainer open(Path path) throws IOException {
    ReadMetrics m = new ReadMetrics();
    return new IliContainer(new LocalSource(path, m), m, 32L * 1024 * 1024);
  }

  public static IliContainer open(URI uri) throws IOException {
    return open(uri, new RemoteOptions());
  }

  public static IliContainer open(URI uri, RemoteOptions options) throws IOException {
    if ("file".equals(uri.getScheme())) return open(Paths.get(uri));
    ReadMetrics m = new ReadMetrics();
    return new IliContainer(new HttpRangeSource(uri, options, m), m, options.cacheBytes);
  }

  private IliContainer(RangeSource source, ReadMetrics metrics, long cache) throws IOException {
    this.source = source;
    this.metrics = metrics;
    store = new FrameStore(source, metrics, cache);
    try {
      int formatVersion =
          Frames.checkHeader(
              new DataInputStream(new ByteArrayInputStream(source.read(0, Frames.HEADER_SIZE))));
      roots = Frames.footer(source);
      Frames.Frame m = store.read(Frames.HEADER_SIZE);
      if (m.type != Frames.METADATA) throw new IOException("Missing metadata");
      metadata = Cbor.read(m.data, TransferMetadata.class);
      if (!"2.4".equals(metadata.version) || metadata.mappingVersion != 1)
        throw new IOException("Unsupported transfer/mapping version");
      metadata.validateFormat(formatVersion);
      codec = new ObjectCodec(metadata, true);
      tree = new BTree(store, roots[0]);
    } catch (IOException e) {
      source.close();
      throw e;
    }
  }

  public void checkOpen() {
    if (closed) throw new IllegalStateException("Container closed");
  }

  public TransferMetadata metadata() {
    checkOpen();
    return metadata;
  }

  public ReadMetrics metrics() {
    return metrics;
  }

  public FrameStore frameStore() {
    return store;
  }

  public long indexRoot() {
    return roots[0];
  }

  public long spatialRoot() {
    return roots[1];
  }

  public long size() throws IOException {
    return source.size();
  }

  public void clearCache() {
    store.clear();
  }

  public IoxReader openTransferReader() throws IOException {
    checkOpen();
    return new SequentialReader(new RangeInputStream(source));
  }

  public static IoxReader stream(InputStream input) throws IOException {
    return new SequentialReader(input);
  }

  private CloseableIterator<Location> range(String prefix) throws IOException {
    final CloseableIterator<ExternalSort.Entry> it = tree.range(prefix);
    return new CloseableIterator<Location>() {
      public boolean hasNext() {
        checkOpen();
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
        it.close();
      }
    };
  }

  public List<String> layers() {
    checkOpen();
    if (!"wkb".equals(metadata.geometryEncoding))
      throw new IllegalStateException("GIS API requires WKB geometry profile");
    List<String> layers = new ArrayList<String>();
    for (String id : metadata.geometries.keySet())
      if (metadata.concreteClasses.contains(id.substring(0, id.lastIndexOf('.')))) layers.add(id);
    return Collections.unmodifiableList(layers);
  }

  public GisLayer openLayer(String id) {
    if (!layers().contains(id)) throw new IllegalArgumentException("Unknown GIS layer " + id);
    return new GisLayer(this, id);
  }

  Fragment getFid(long fid) {
    checkOpen();
    return new Fragment(
        this,
        () -> singleton(fid < 0 ? null : tree.get("F\0" + FilesEx.number(fid))),
        "FID " + fid);
  }

  public Fragment getTopic(String name) {
    checkOpen();
    if (!metadata.topics.contains(name))
      throw new IllegalArgumentException("Unknown topic: " + name);
    return new Fragment(this, () -> range("T\0" + name + "\0"), "topic " + name);
  }

  public Fragment getClass(String name) {
    checkOpen();
    if (!metadata.classes.containsKey(name))
      throw new IllegalArgumentException("Unknown class: " + name);
    return new Fragment(this, () -> range("C\0" + name + "\0"), "class " + name);
  }

  public Fragment getObject(String tid) {
    checkOpen();
    return new Fragment(this, () -> singleton(tree.get("O\0" + tid)), "object " + tid);
  }

  public Fragment getBasket(String bid) {
    checkOpen();
    return new Fragment(
        this,
        () -> {
          byte[] value = tree.get("B\0" + bid);
          if (value == null) return singleton(null);
          Location loc = Cbor.read(value, Location.class);
          final CloseableIterator<Location> rest =
              range("D\0" + FilesEx.number(loc.basketPosition) + "\0");
          return new CloseableIterator<Location>() {
            boolean first = true;

            public boolean hasNext() {
              return first || rest.hasNext();
            }

            public Location next() {
              if (first) {
                first = false;
                return loc;
              }
              return rest.next();
            }

            public void close() throws IOException {
              rest.close();
            }
          };
        },
        "basket " + bid);
  }

  private static CloseableIterator<Location> singleton(byte[] bytes) throws IOException {
    final Location loc = bytes == null ? null : Cbor.read(bytes, Location.class);
    return new CloseableIterator<Location>() {
      boolean available = loc != null;

      public boolean hasNext() {
        return available;
      }

      public Location next() {
        if (!available) throw new NoSuchElementException();
        available = false;
        return loc;
      }

      public void close() {
        available = false;
      }
    };
  }

  public BasketContext basket(Location loc) throws IOException {
    checkOpen();
    Frames.Frame f = store.read(loc.basketOffset);
    if (f.type != Frames.BASKET) throw new IOException("Invalid basket reference");
    BasketContext b = Cbor.read(f.data, BasketContext.class);
    if (b.position != loc.basketPosition) throw new IOException("Basket position mismatch");
    return b;
  }

  public ObjectCursor objects(Location loc) throws IOException {
    checkOpen();
    Frames.Frame f = store.read(loc.chunkOffset);
    if (f.type != Frames.CHUNK) throw new IOException("Invalid chunk reference");
    Chunk c = Chunk.unpack(f.data);
    if (c.info.id != loc.chunkId
        || c.info.basketPosition != loc.basketPosition
        || c.info.basketOffset != loc.basketOffset
        || loc.ordinal >= c.info.count) throw new IOException("Invalid object/chunk reference");
    return new ObjectCursor(c, codec);
  }

  public Fragment querySpatialCandidates(String className, String attribute, BoundingBox box)
      throws IOException {
    checkOpen();
    return ch.interlis.ilicontainer.spatial.SpatialIndex.query(this, className, attribute, box);
  }

  public void export(OutputStream output) throws Exception {
    XtfWriterBase writer = ModelBridge.writer(output, metadata);
    IoxReader reader = openTransferReader();
    try {
      IoxEvent e;
      while ((e = reader.read()) != null) writer.write(e);
      writer.flush();
    } finally {
      reader.close();
    } // caller owns output
  }

  public void exportFragment(Fragment fragment, OutputStream output) throws Exception {
    XtfWriterBase writer = ModelBridge.writer(output, metadata);
    ch.interlis.iom_j.xtf.XtfStartTransferEvent start = metadata.event();
    start.setComment(
        "IliContainer fragment; "
            + fragment.description()
            + "; may be incomplete and not model-conformant."
            + (metadata.comment == null ? "" : "\n" + metadata.comment));
    writer.write(start);
    try (Stream<BasketContext> bs = fragment.baskets();
        Stream<SelectedObject> os = fragment.objects()) {
      Iterator<SelectedObject> objects = os.iterator();
      SelectedObject next = objects.hasNext() ? objects.next() : null;
      Iterator<BasketContext> baskets = bs.iterator();
      while (baskets.hasNext()) {
        BasketContext basket = baskets.next();
        writer.write(basket.event());
        while (next != null && next.getBasket().position == basket.position) {
          writer.write(new ch.interlis.iox_j.ObjectEvent(next.getObject()));
          next = objects.hasNext() ? objects.next() : null;
        }
        writer.write(new ch.interlis.iox_j.EndBasketEvent());
      }
      if (next != null) throw new IOException("Fragment object without basket");
    }
    writer.write(new ch.interlis.iox_j.EndTransferEvent());
    writer.flush();
  }

  public void close() throws IOException {
    if (!closed) {
      closed = true;
      store.clear();
      source.close();
    }
  }
}
