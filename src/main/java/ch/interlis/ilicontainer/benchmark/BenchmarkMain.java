package ch.interlis.ilicontainer.benchmark;

import ch.interlis.ilicontainer.api.*;
import ch.interlis.ilicontainer.container.*;
import ch.interlis.ilicontainer.iox.ModelBridge;
import ch.interlis.ilicontainer.spatial.*;
import ch.interlis.iom.IomObject;
import ch.interlis.iom_j.xtf.Xtf24Reader;
import ch.interlis.iox.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.luben.zstd.*;
import java.io.*;
import java.lang.management.*;
import java.nio.file.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.Callable;
import java.util.stream.Stream;
import java.util.zip.*;
import picocli.CommandLine;
import picocli.CommandLine.*;

@Command(name = "ilic-benchmark", mixinStandardHelpOptions = true)
public final class BenchmarkMain implements Callable<Integer> {
  @Option(names = "--input", required = true)
  Path input;

  @Option(names = "--output", required = true)
  Path output;

  @Option(names = "--model-dir")
  List<String> modelDirs = new ArrayList<String>();

  @Option(names = "--model-file")
  List<String> modelFiles = new ArrayList<String>();

  @Option(names = "--class", required = true)
  String cls;

  @Option(names = "--geometry", required = true)
  String geometry;

  @Option(names = "--crs", required = true)
  String crs;

  @Option(
      names = "--matrix",
      description = "Both numeric codecs and 64 KiB, 256 KiB, 1 MiB, 4 MiB chunks")
  boolean matrix;

  @Option(
      names = "--refresh-spatial",
      description = "Remeasure spatial indexes/access against existing verified core results")
  boolean refreshSpatial;

  @Option(
      names = "--reuse-identical-access",
      description =
          "With --refresh-spatial, retain access timings only when rebuilt bytes have the same"
              + " SHA-256")
  boolean reuseIdenticalAccess;

  @Option(names = "--repeats", defaultValue = "3")
  int repeats;

  private final List<Map<String, Object>> rows = new ArrayList<Map<String, Object>>();
  private TransferMetadata modelMetadata;
  private String firstTid, firstBid;
  private BoundingBox extent;

  public static void main(String[] args) {
    System.exit(new CommandLine(new BenchmarkMain()).execute(args));
  }

  private WriterOptions options() {
    WriterOptions w = new WriterOptions();
    w.modelPaths.addAll(modelDirs);
    w.modelFiles.addAll(modelFiles);
    return w;
  }

  public Integer call() throws Exception {
    if (repeats < 1) throw new IllegalArgumentException("repeats must be positive");
    Files.createDirectories(output);
    if (refreshSpatial) return refreshSpatialResults();
    if (reuseIdenticalAccess)
      throw new IllegalArgumentException("--reuse-identical-access requires --refresh-spatial");
    Path temp = Files.createTempDirectory(output, "models-");
    try {
      ModelBridge bridge = ModelBridge.load(input, options(), temp);
      modelMetadata = bridge.metadata;
      Path zip = output.resolve("baseline.xtf.zip"), zst = output.resolve("baseline.xtf.zst");
      try (OutputStream out = Files.newOutputStream(zip);
          ZipOutputStream compressed = new ZipOutputStream(out);
          InputStream in = Files.newInputStream(input)) {
        ZipEntry e = new ZipEntry("data.xtf");
        e.setTime(0);
        compressed.putNextEntry(e);
        copy(in, compressed);
        compressed.closeEntry();
      }
      try (OutputStream out = Files.newOutputStream(zst);
          ZstdOutputStream compressed = new ZstdOutputStream(out, 3);
          InputStream in = Files.newInputStream(input)) {
        copy(in, compressed);
      }
      for (int r = 0; r < repeats; r++)
        for (Path file : Arrays.asList(input, zip, zst)) {
          try (InputStream raw = Files.newInputStream(file)) {
            InputStream source = raw;
            if (file.equals(zip)) {
              ZipInputStream z = new ZipInputStream(raw);
              z.getNextEntry();
              source = z;
            } else if (file.equals(zst)) source = new ZstdInputStream(raw);
            try (InputStream decoded = source) {
              Xtf24Reader reader = new Xtf24Reader(decoded);
              reader.setModel(bridge.model);
              Map<String, Object> row = scan(reader);
              row.put(
                  "variant", file.equals(input) ? "XTF" : file.equals(zip) ? "XTF.zip" : "XTF.zst");
              row.put("repeat", r);
              row.put("fileBytes", Files.size(file));
              row.put(
                  "sourceMiBPerSecond",
                  Files.size(file) / 1048576.0 / ((Double) row.get("wallMillis") / 1000));
              rows.add(row);
            }
          }
        }
      int[] sizes = matrix ? new int[] {65536, 262144, 1048576, 4194304} : new int[] {262144};
      String[] codecs = matrix ? new String[] {"lexical", "decimal"} : new String[] {"lexical"};
      for (String codec : codecs)
        for (int size : sizes) {
          String variant = codec + "-" + size;
          Path core = output.resolve(variant + ".ilic");
          WriterOptions w = options();
          w.numericEncoding = codec;
          w.chunkSize = size;
          w.overwrite = true;
          Meter meter = new Meter();
          ContainerWriter.create(input, core, w);
          Map<String, Object> creation = meter.finish(0, -1);
          creation.put("temporaryPeakSampledBytes", w.temporaryPeakSampledBytes);
          creation.put("objectDirectoryEntryBytes", w.objectDirectoryEntryBytes);
          creation.put("operation", "create");
          creation.put("variant", variant);
          creation.put("fileBytes", Files.size(core));
          rows.add(creation);
          Path roundtrip = output.resolve(variant + "-roundtrip.xtf");
          try (IliContainer c = IliContainer.open(core);
              OutputStream exported = new BufferedOutputStream(Files.newOutputStream(roundtrip))) {
            c.export(exported);
          }
          long verified = RoundtripVerifier.verify(input, roundtrip, bridge, temp);
          creation.put("semanticRoundtripRecords", verified);
          Files.delete(roundtrip);
          for (int r = 0; r < repeats; r++) {
            try (InputStream in = Files.newInputStream(core)) {
              Map<String, Object> row = scan(IliContainer.stream(in));
              row.put("variant", variant);
              row.put("repeat", r);
              row.put("fileBytes", Files.size(core));
              row.put(
                  "sourceMiBPerSecond",
                  Files.size(core) / 1048576.0 / ((Double) row.get("wallMillis") / 1000));
              rows.add(row);
            }
          }
          try (IliContainer c = IliContainer.open(core);
              Fragment f = c.getClass(cls);
              Stream<SelectedObject> stream = f.objects()) {
            Iterator<SelectedObject> it = stream.iterator();
            while (it.hasNext()) {
              SelectedObject selected = it.next();
              BoundingBox box = GeometryBounds.attribute(selected.getObject(), geometry);
              if (box != null) {
                if (extent == null) extent = box;
                else extent.expand(box);
              }
            }
          }
          if (extent == null) throw new IOException("No geometry for benchmark class");
          access(core, variant, false);
          Path spatial = output.resolve(variant + "-spatial.ilic");
          Files.copy(core, spatial, StandardCopyOption.REPLACE_EXISTING);
          meter = new Meter();
          SpatialIndex.add(spatial, cls, geometry, crs);
          Map<String, Object> index = meter.finish(0, -1);
          index.put("operation", "build-spatial");
          index.put("variant", variant);
          index.put("fileBytes", Files.size(spatial));
          index.put("spatialOverheadBytes", Files.size(spatial) - Files.size(core));
          rows.add(index);
          access(spatial, variant + "-spatial", true);
          writeReport();
        }
      writeReport();
      return 0;
    } finally {
      FilesEx.deleteTree(temp);
    }
  }

  @SuppressWarnings("unchecked")
  private Integer refreshSpatialResults() throws Exception {
    Map<String, Object> old =
        new ObjectMapper().readValue(output.resolve("results.json").toFile(), Map.class);
    if (!PrepareData.digest(input).equals(old.get("inputSha256"))
        || !cls.equals(old.get("queryClass"))
        || !geometry.equals(old.get("geometry"))
        || !crs.equals(old.get("crs")))
      throw new IOException("Existing benchmark identity differs");
    firstTid = (String) old.get("firstTid");
    firstBid = (String) old.get("firstBid");
    extent = new ObjectMapper().convertValue(old.get("extent"), BoundingBox.class);
    List<String> variants = new ArrayList<String>();
    Map<String, List<Map<String, Object>>> oldAccess =
        new HashMap<String, List<Map<String, Object>>>();
    for (Map<String, Object> row : (List<Map<String, Object>>) old.get("rows")) {
      String variant = (String) row.get("variant");
      if ("create".equals(row.get("operation"))) variants.add(variant);
      if (variant.endsWith("-spatial")) {
        List<Map<String, Object>> group = oldAccess.get(variant);
        if (group == null) {
          group = new ArrayList<Map<String, Object>>();
          oldAccess.put(variant, group);
        }
        group.add(row);
      }
      if (!variant.endsWith("-spatial") && !"build-spatial".equals(row.get("operation")))
        rows.add(row);
    }
    if (variants.size() != (matrix ? 8 : 1)) throw new IOException("Existing matrix is incomplete");
    for (String variant : variants) {
      Path core = output.resolve(variant + ".ilic"),
          spatial = output.resolve(variant + "-spatial.ilic");
      if (modelMetadata == null) {
        try (IliContainer container = IliContainer.open(core)) {
          modelMetadata = container.metadata();
        }
      }
      String oldDigest =
          reuseIdenticalAccess && Files.exists(spatial) ? PrepareData.digest(spatial) : null;
      Files.copy(core, spatial, StandardCopyOption.REPLACE_EXISTING);
      Meter meter = new Meter();
      SpatialIndex.add(spatial, cls, geometry, crs);
      Map<String, Object> index = meter.finish(0, -1);
      index.put("operation", "build-spatial");
      index.put("variant", variant);
      index.put("fileBytes", Files.size(spatial));
      index.put("spatialOverheadBytes", Files.size(spatial) - Files.size(core));
      rows.add(index);
      List<Map<String, Object>> priorAccess = oldAccess.get(variant + "-spatial");
      boolean identical =
          oldDigest != null
              && oldDigest.equals(PrepareData.digest(spatial))
              && priorAccess != null
              && priorAccess.size() == 24 * repeats;
      index.put("spatialAccessReusedForIdenticalBytes", identical);
      if (identical) rows.addAll(priorAccess);
      else access(spatial, variant + "-spatial", true);
    }
    writeReport();
    return 0;
  }

  private Map<String, Object> scan(IoxReader reader) throws Exception {
    Meter meter = new Meter();
    long count = 0, first = -1;
    try {
      IoxEvent e;
      while ((e = reader.read()) != null) {
        if (e instanceof StartBasketEvent && firstBid == null)
          firstBid = ((StartBasketEvent) e).getBid();
        if (e instanceof ObjectEvent) {
          if (first < 0) first = System.nanoTime() - meter.start;
          IomObject o = ((ObjectEvent) e).getIomObject();
          if (firstTid == null && o.getobjectoid() != null) firstTid = o.getobjectoid();
          count++;
        }
        if (e instanceof EndTransferEvent) break;
      }
    } finally {
      reader.close();
    }
    Map<String, Object> row = meter.finish(count, first);
    row.put("operation", "scan");
    return row;
  }

  private void access(Path file, String variant, boolean spatial) throws Exception {
    try (RangeServer server = new RangeServer(file)) {
      for (boolean remote : new boolean[] {false, true})
        for (int r = 0; r < repeats; r++)
          for (String query :
              spatial
                  ? Arrays.asList(
                      "object", "basket", "class", "bbox-small", "bbox-medium", "bbox-large")
                  : Arrays.asList("object", "basket", "class")) {
            try (IliContainer c =
                remote ? IliContainer.open(server.uri()) : IliContainer.open(file)) {
              for (String cache : Arrays.asList("cold", "warm")) {
                if (cache.equals("cold")) c.clearCache();
                c.metrics().reset();
                Meter meter = new Meter();
                long first = -1, count = 0;
                try (Fragment f = select(c, query);
                    Stream<SelectedObject> objects = f.objects()) {
                  Iterator<SelectedObject> it = objects.iterator();
                  while (it.hasNext()) {
                    it.next();
                    if (first < 0) first = System.nanoTime() - meter.start;
                    count++;
                  }
                }
                Map<String, Object> row = meter.finish(count, first);
                row.put("operation", query);
                row.put("variant", variant);
                row.put("remote", remote);
                row.put("cache", cache);
                row.put("repeat", r);
                ReadMetrics m = c.metrics();
                row.put("bytesRead", m.bytesRead);
                row.put("requests", m.requests);
                row.put("indexBytes", m.indexBytes);
                row.put("chunkBytes", m.chunkBytes);
                row.put("chunks", m.chunksRead);
                row.put("cacheHits", m.cacheHits);
                rows.add(row);
              }
            }
          }
    }
  }

  private Fragment select(IliContainer c, String query) throws Exception {
    if (query.equals("object")) return c.getObject(firstTid);
    if (query.equals("basket")) return c.getBasket(firstBid);
    if (query.equals("class")) return c.getClass(cls);
    double fraction = query.endsWith("small") ? .01 : query.endsWith("medium") ? .1 : 1.0;
    double cx = (extent.minX + extent.maxX) / 2,
        cy = (extent.minY + extent.maxY) / 2,
        dx = (extent.maxX - extent.minX) * fraction / 2,
        dy = (extent.maxY - extent.minY) * fraction / 2;
    return c.querySpatialCandidates(
        cls, geometry, new BoundingBox(cx - dx, cy - dy, cx + dx, cy + dy));
  }

  private void writeReport() throws Exception {
    Map<String, Object> report = new LinkedHashMap<String, Object>();
    report.put("createdAt", Instant.now().toString());
    report.put(
        "arcEnclosure", "exact decimal orientation, rational centre and directed radius bounds");
    report.put("input", input.toAbsolutePath().toString());
    report.put("inputSha256", PrepareData.digest(input));
    report.put("java", System.getProperty("java.version"));
    if (modelMetadata != null) {
      report.put("models", modelMetadata.models);
      report.put("modelSources", modelMetadata.sources);
    }
    report.put("os", System.getProperty("os.name") + " " + System.getProperty("os.arch"));
    report.put("osVersion", System.getProperty("os.version"));
    report.put("availableProcessors", Runtime.getRuntime().availableProcessors());
    report.put("maxHeapBytes", Runtime.getRuntime().maxMemory());
    report.put("queryClass", cls);
    report.put("geometry", geometry);
    report.put("crs", crs);
    report.put("firstTid", firstTid);
    report.put("firstBid", firstBid);
    report.put("extent", extent);
    report.put("bboxLinearFractions", Arrays.asList(.01, .1, 1.0));
    report.put(
        "cachePolicy",
        "cold/warm application cache; OS cache uncontrolled; metadata bootstrap excluded from query"
            + " metrics");
    report.put("remoteEnvironment", "loopback static HTTP fixture; network latency not simulated");
    report.put("rows", rows);
    new ObjectMapper()
        .writerWithDefaultPrettyPrinter()
        .writeValue(output.resolve("results.json").toFile(), report);
    StringBuilder md =
        new StringBuilder(
            "# IliContainer benchmark\n\nInput SHA-256: `"
                + report.get("inputSha256")
                + "`\n\nJava "
                + report.get("java")
                + ", "
                + report.get("os")
                + ". Remote: loopback. Cold/warm refers to the application cache; OS caches are"
                + " uncontrolled. Query metrics exclude opening metadata.\n\n"
                + "| Variant | Operation | Remote | Cache | Objects | ms | Bytes read | Requests |"
                + " File bytes |\n"
                + "|---|---|---|---|---:|---:|---:|---:|---:|\n");
    for (Map<String, Object> r : rows)
      md.append("| ")
          .append(r.get("variant"))
          .append(" | ")
          .append(r.get("operation"))
          .append(" | ")
          .append(r.getOrDefault("remote", "—"))
          .append(" | ")
          .append(r.getOrDefault("cache", "—"))
          .append(" | ")
          .append(r.get("objects"))
          .append(" | ")
          .append(String.format(Locale.ROOT, "%.3f", r.get("wallMillis")))
          .append(" | ")
          .append(r.getOrDefault("bytesRead", "—"))
          .append(" | ")
          .append(r.getOrDefault("requests", "—"))
          .append(" | ")
          .append(r.getOrDefault("fileBytes", "—"))
          .append(" |\n");
    Files.write(output.resolve("results.md"), md.toString().getBytes("UTF-8"));
  }

  private static void copy(InputStream in, OutputStream out) throws IOException {
    byte[] b = new byte[65536];
    int n;
    while ((n = in.read(b)) != -1) out.write(b, 0, n);
  }

  private static final class Meter {
    final long start = System.nanoTime(),
        cpu = ManagementFactory.getThreadMXBean().getCurrentThreadCpuTime();

    Meter() {
      for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans())
        if (pool.getType() == MemoryType.HEAP) pool.resetPeakUsage();
    }

    Map<String, Object> finish(long objects, long first) {
      Map<String, Object> r = new LinkedHashMap<String, Object>();
      long elapsed = System.nanoTime() - start;
      r.put("objects", objects);
      r.put("wallMillis", elapsed / 1e6);
      r.put(
          "cpuMillis", (ManagementFactory.getThreadMXBean().getCurrentThreadCpuTime() - cpu) / 1e6);
      r.put("firstObjectMillis", first < 0 ? null : first / 1e6);
      r.put("objectsPerSecond", objects * 1e9 / Math.max(1, elapsed));
      long heap = 0;
      for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans())
        if (pool.getType() == MemoryType.HEAP) heap += pool.getPeakUsage().getUsed();
      r.put("peakHeapPoolSumBytes", heap);
      return r;
    }
  }
}
