package ch.interlis.ibx.benchmark;

import ch.interlis.ibx.api.*;
import ch.interlis.ibx.container.*;
import ch.interlis.ibx.iox.ModelBridge;
import ch.interlis.ibx.spatial.*;
import ch.interlis.iox.*;
import com.fasterxml.jackson.databind.*;
import java.io.*;
import java.lang.management.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

/**
 * Isolated comparison worker. New API options are reflected so the same worker runs with the
 * reference JAR.
 */
public final class OptimizationBenchmark {
  private static final ObjectMapper JSON = new ObjectMapper();
  private final JsonNode config;
  private final Path output, container;
  private final String cls, attribute;
  private final boolean reference;
  private final boolean directoryOnly;
  private final List<Map<String, Object>> rows = new ArrayList<Map<String, Object>>();
  private List<BoundingBox> windows = new ArrayList<BoundingBox>();
  private String tid;
  private long fid = -1;

  private OptimizationBenchmark(JsonNode config) {
    this.config = config;
    output = Paths.get(config.get("output").asText());
    container = output.resolve("data.ibx");
    cls = config.get("class").asText();
    attribute = config.get("attribute").asText();
    reference = config.path("reference").asBoolean();
    directoryOnly = config.path("directoryOnly").asBoolean();
  }

  public static void main(String[] args) throws Exception {
    new OptimizationBenchmark(JSON.readTree(Paths.get(args[0]).toFile())).run();
  }

  private static String digest(Path path) throws Exception {
    java.security.MessageDigest digest = java.security.MessageDigest.getInstance("SHA-256");
    try (InputStream in = Files.newInputStream(path)) {
      byte[] b = new byte[65536];
      int n;
      while ((n = in.read(b)) >= 0) digest.update(b, 0, n);
    }
    StringBuilder text = new StringBuilder();
    for (byte b : digest.digest()) text.append(String.format(Locale.ROOT, "%02x", b & 255));
    return text.toString();
  }

  private static void set(Object object, String field, Object value) throws Exception {
    object.getClass().getField(field).set(object, value);
  }

  private static long heap() {
    long sum = 0;
    for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans())
      if (pool.getType() == MemoryType.HEAP) sum += pool.getPeakUsage().getUsed();
    return sum;
  }

  private static void resetHeap() {
    for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans()) pool.resetPeakUsage();
  }

  private Map<String, Object> row(String operation, long start, long count, ReadMetrics metrics) {
    Map<String, Object> row = new LinkedHashMap<String, Object>();
    row.put("operation", operation);
    row.put("millis", (System.nanoTime() - start) / 1e6);
    row.put("count", count);
    row.put("heapPeakPoolSumBytes", heap());
    if (metrics != null) row.put("metrics", JSON.convertValue(metrics, Map.class));
    rows.add(row);
    return row;
  }

  private void save() throws Exception {
    Map<String, Object> report = new LinkedHashMap<String, Object>();
    report.put("parameters", config);
    report.put("rows", rows);
    report.put("windows", windows);
    report.put("java", System.getProperty("java.version"));
    report.put("maxHeapBytes", Runtime.getRuntime().maxMemory());
    Path jar =
        Paths.get(IbxContainer.class.getProtectionDomain().getCodeSource().getLocation().toURI());
    report.put("librarySha256", digest(jar));
    Path tmp = output.resolve("results.tmp");
    JSON.writerWithDefaultPrettyPrinter().writeValue(tmp.toFile(), report);
    Files.move(tmp, output.resolve("results.json"), StandardCopyOption.REPLACE_EXISTING);
  }

  @SuppressWarnings("unchecked")
  private void run() throws Exception {
    Files.createDirectories(output);
    Path input = Paths.get(config.get("input").asText()),
        work = Files.createTempDirectory(output, "work-");
    try {
      WriterOptions w = new WriterOptions();
      w.overwrite = true;
      w.geometryEncoding = config.get("encoding").asText();
      w.chunkSize = config.get("chunkSize").asInt();
      w.numericEncoding = "lexical";
      w.compressionLevel = 3;
      for (JsonNode path : config.path("modelPaths")) w.modelPaths.add(path.asText());
      for (JsonNode path : config.path("modelFiles")) w.modelFiles.add(path.asText());
      ModelBridge model = ModelBridge.load(input, w, work);
      for (Map.Entry<String, String> entry : model.metadata.geometryCrs.entrySet())
        if (entry.getValue().isEmpty())
          w.geometryCrs.put(entry.getKey(), config.path("crs").asText("EPSG:2056"));
      if (!reference && config.path("hilbert").asBoolean())
        ((Map<String, String>) w.getClass().getField("spatialOrder").get(w)).put(cls, attribute);
      resetHeap();
      long start = System.nanoTime();
      ContainerWriter.create(input, container, w);
      Map<String, Object> creation = row("create", start, 0, null);
      creation.put("fileBytes", Files.size(container));
      creation.put("temporaryPeakSampledBytes", w.temporaryPeakSampledBytes);
      creation.put("inputSha256", digest(input));
      creation.put("inputBytes", Files.size(input));
      start = System.nanoTime();
      if (!directoryOnly) {
        if (reference)
          SpatialIndex.add(container, cls, attribute, config.path("crs").asText("EPSG:2056"));
        else {
          Class<?> type = Class.forName("ch.interlis.ibx.api.SpatialIndexOptions");
          Object opts = type.newInstance();
          set(opts, "packing", config.get("packing").asText());
          SpatialIndex.class
              .getMethod("add", Path.class, String.class, String.class, String.class, type)
              .invoke(
                  null, container, cls, attribute, config.path("crs").asText("EPSG:2056"), opts);
        }
      }
      Map<String, Object> indexing = row(directoryOnly ? "directory" : "index", start, 0, null);
      indexing.put("fileBytes", Files.size(container));
      if (!reference)
        try (IbxContainer c = IbxContainer.open(container)) {
          Object stats =
              Class.forName("ch.interlis.ibx.container.StorageDiagnostics")
                  .getMethod("inspect", IbxContainer.class)
                  .invoke(null, c);
          indexing.put("storage", stats);
        }
      Path exported = output.resolve("roundtrip.xtf");
      resetHeap();
      start = System.nanoTime();
      try (IbxContainer c = IbxContainer.open(container);
          OutputStream out = new BufferedOutputStream(Files.newOutputStream(exported))) {
        c.export(out);
      }
      row("export", start, 0, null);
      if (config.path("controlsOnly").asBoolean()) {
        Files.delete(exported);
        save();
        Files.write(output.resolve("complete"), new byte[0]);
        return;
      }
      start = System.nanoTime();
      long checked = RoundtripVerifier.verify(input, exported, model, work);
      row("roundtrip", start, checked, null);
      Files.delete(exported);
      prepareQueries();
      save();
      for (int repeat = 0; repeat < config.path("repeats").asInt(3); repeat++) {
        resetHeap();
        start = System.nanoTime();
        long count = 0;
        IoxReader reader = IbxContainer.stream(Files.newInputStream(container));
        try {
          IoxEvent e;
          while ((e = reader.read()) != null) if (e instanceof ObjectEvent) count++;
        } finally {
          reader.close();
        }
        row("scan", start, count, null).put("repeat", repeat);
      }
      for (int delay : new int[] {-1, 0, 20, 80}) {
        if (config.has("delays") && !contains(config.get("delays"), delay)) continue;
        try (RangeServer server = new RangeServer(container)) {
          server.delayMillis = Math.max(0, delay);
          for (int repeat = 0; repeat < config.path("repeats").asInt(3); repeat++) {
            List<String> queries =
                new ArrayList<String>(
                    directoryOnly
                        ? Arrays.asList("tid", "fid")
                        : Arrays.asList("tid", "fid", "class"));
            for (int i = 0; i < windows.size(); i++) queries.add("bbox-" + i);
            for (String query : queries) {
              if (query.equals("fid")
                  && (reference && !w.geometryEncoding.equals("wkb") || fid < 0)) {
                Map<String, Object> missing = row("fid", System.nanoTime(), 0, null);
                missing.put("unavailable", true);
                continue;
              }
              RemoteOptions remote = new RemoteOptions();
              if (!reference)
                set(remote, "prefetchPositions", config.path("prefetch").asBoolean() ? 32 : 0);
              long openStart = System.nanoTime();
              try (IbxContainer c =
                  delay < 0
                      ? openLocal(container, remote)
                      : IbxContainer.open(server.uri(), remote)) {
                Map<String, Object> opening = row("open", openStart, 0, c.metrics());
                label(opening, query, delay, repeat, "cold");
                for (String cache : Arrays.asList("cold", "warm")) {
                  if (cache.equals("cold")) c.clearCache();
                  c.metrics().reset();
                  resetHeap();
                  start = System.nanoTime();
                  long count = query(c, query, w.geometryEncoding.equals("wkb"));
                  label(row("query", start, count, c.metrics()), query, delay, repeat, cache);
                }
              }
              save();
            }
          }
        }
      }
      save();
      Files.write(output.resolve("complete"), new byte[0]);
    } finally {
      FilesEx.deleteTree(work);
    }
  }

  private static boolean contains(JsonNode values, int wanted) {
    for (JsonNode n : values) if (n.asInt() == wanted) return true;
    return false;
  }

  private void label(Map<String, Object> row, String query, int delay, int repeat, String cache) {
    row.put("query", query);
    row.put("delayMillis", delay);
    row.put("repeat", repeat);
    row.put("cache", cache);
  }

  private IbxContainer openLocal(Path path, RemoteOptions options) throws Exception {
    if (reference) return IbxContainer.open(path);
    return (IbxContainer)
        IbxContainer.class
            .getMethod("open", Path.class, RemoteOptions.class)
            .invoke(null, path, options);
  }

  private long query(IbxContainer c, String query, boolean gis) throws Exception {
    if (query.equals("tid"))
      try (Fragment f = c.getObject(tid);
          Stream<SelectedObject> stream = f.objects()) {
        return stream.count();
      }
    if (query.equals("fid") && !gis) {
      try (Fragment f =
              (Fragment) IbxContainer.class.getMethod("getFid", long.class).invoke(c, fid);
          Stream<SelectedObject> stream = f.objects()) {
        return stream.count();
      }
    }
    if (gis)
      try (GisLayer layer = c.openLayer(cls + "." + attribute)) {
        if (query.equals("fid")) return layer.getFeature(fid).isPresent() ? 1 : 0;
        try (Stream<GisFeature> stream =
            query.equals("class")
                ? layer.features()
                : layer.queryCandidates(windows.get(Integer.parseInt(query.substring(5))))) {
          return stream.count();
        }
      }
    try (Fragment f =
            query.equals("class")
                ? c.getClass(cls)
                : c.querySpatialCandidates(
                    cls, attribute, windows.get(Integer.parseInt(query.substring(5))));
        Stream<SelectedObject> stream = f.objects()) {
      return stream.count();
    }
  }

  private void prepareQueries() throws Exception {
    BoundingBox extent = null;
    List<BoundingBox> samples = new ArrayList<BoundingBox>();
    Random random = new Random(20260917);
    long seen = 0;
    try (IbxContainer c = IbxContainer.open(container);
        Fragment f = c.getClass(cls);
        Stream<SelectedObject> stream = f.objects()) {
      Iterator<SelectedObject> it = stream.iterator();
      while (it.hasNext()) {
        SelectedObject object = it.next();
        if (tid == null) tid = object.getObject().getobjectoid();
        if (directoryOnly) break;
        BoundingBox box = GeometryBounds.attribute(object.getObject(), attribute);
        if (box == null) continue;
        if (extent == null) extent = new BoundingBox(box.minX, box.minY, box.maxX, box.maxY);
        else extent.expand(box);
        seen++;
        if (samples.size() < 20) samples.add(box);
        else {
          long selected = (long) (random.nextDouble() * seen);
          if (selected < 20) samples.set((int) selected, box);
        }
      }
    }
    if (!directoryOnly) {
      if (extent == null) throw new IOException("No benchmark geometry");
      for (double scale : new double[] {.01, .1, 1.0}) windows.add(window(extent, extent, scale));
      for (int i = 0; i < 20; i++)
        windows.add(
            window(samples.get(i % samples.size()), extent, .002 + random.nextDouble() * .018));
      // A single reference query manifest fixes both object identity and windows across variants.
      if (config.has("windowsFile")
          && Files.exists(Paths.get(config.get("windowsFile").asText()))) {
        JsonNode queries = JSON.readTree(Paths.get(config.get("windowsFile").asText()).toFile());
        windows.clear();
        tid = queries.get("tid").asText();
        for (JsonNode box : queries.get("windows"))
          windows.add(JSON.treeToValue(box, BoundingBox.class));
      } else if (config.has("windowsFile")) {
        Map<String, Object> queries = new LinkedHashMap<String, Object>();
        queries.put("tid", tid);
        queries.put("windows", windows);
        JSON.writerWithDefaultPrettyPrinter()
            .writeValue(Paths.get(config.get("windowsFile").asText()).toFile(), queries);
      }
    }
    try (IbxContainer c = IbxContainer.open(container);
        Fragment f = c.getObject(tid);
        CloseableIterator<Location> refs = f.locations()) {
      if (refs.hasNext()) {
        Location loc = refs.next();
        try (ObjectCursor cursor = c.objects(loc)) {
          if (cursor.firstFid >= 0) fid = cursor.firstFid + loc.ordinal;
        }
      }
    }
  }

  private static BoundingBox window(BoundingBox center, BoundingBox extent, double scale) {
    double x = center.minX / 2 + center.maxX / 2, y = center.minY / 2 + center.maxY / 2;
    double dx = (extent.maxX - extent.minX) * scale / 2,
        dy = (extent.maxY - extent.minY) * scale / 2;
    return new BoundingBox(x - dx, y - dy, x + dx, y + dy);
  }
}
