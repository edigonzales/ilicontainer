package ch.interlis.ibx.cli;

import ch.interlis.ibx.api.*;
import ch.interlis.ibx.container.*;
import ch.interlis.ibx.spatial.SpatialIndex;
import java.io.*;
import java.net.URI;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.Callable;
import picocli.CommandLine;
import picocli.CommandLine.*;

@Command(
    name = "ibx",
    mixinStandardHelpOptions = true,
    version = "IBX 0.4.0-prototype",
    description = "INTERLIS 2.3/2.4 FULL chunked transfer container.",
    subcommands = {
      Main.Create.class,
      Main.Info.class,
      Main.Export.class,
      Main.GetTopic.class,
      Main.GetBasket.class,
      Main.GetClass.class,
      Main.GetObject.class,
      Main.Bbox.class,
      Main.Index.class
    })
public final class Main implements Runnable {
  public void run() {
    CommandLine.usage(this, System.out);
  }

  public static int execute(String... args) {
    return new CommandLine(new Main())
        .setExecutionExceptionHandler(
            (ex, cmd, result) -> {
              cmd.getErr().println("Error: " + ex.getMessage());
              return 1;
            })
        .execute(args);
  }

  public static void main(String[] args) {
    System.exit(execute(args));
  }

  @Command(
      name = "create",
      mixinStandardHelpOptions = true,
      description = "Create a FULL container; optional index failure leaves the core intact.")
  public static final class Create implements Callable<Integer> {
    @Parameters(index = "0")
    Path input;

    @Parameters(index = "1")
    Path output;

    @Option(
        names = "--model-dir",
        description = "Local model directory or repository URL; repeatable.")
    List<String> modelDirs = new ArrayList<String>();

    @Option(names = "--model-file")
    List<String> modelFiles = new ArrayList<String>();

    @Option(names = "--embed-models")
    boolean embed;

    @Option(names = "--no-reverse-index")
    boolean noReverseIndex;

    @Option(names = "--overwrite")
    boolean overwrite;

    @Option(names = "--chunk-size", defaultValue = "262144")
    int chunk;

    @Option(names = "--compression", defaultValue = "zstd")
    String compression;

    @Option(names = "--compression-level", defaultValue = "3")
    int level;

    @Option(names = "--numeric-encoding", defaultValue = "lexical")
    String numeric;

    @Option(names = "--geometry-encoding", defaultValue = "iom")
    String geometry;

    @Option(names = "--geometry-crs", description = "Class.Attribute=CRS; repeatable")
    Map<String, String> geometryCrs = new TreeMap<String, String>();

    @Option(
        names = "--spatial",
        description = "Fully qualified class plus geometry attribute, separated by a colon.")
    List<String> indexes = new ArrayList<String>();

    @Option(names = "--spatial-packing", defaultValue = "str")
    String packing;

    @Option(names = "--crs")
    String crs;

    @Option(
        names = "--spatial-order",
        description = "Class.Attribute; repeatable for distinct classes")
    List<String> spatialOrder = new ArrayList<String>();

    public Integer call() throws Exception {
      SpatialIndexOptions spatialOptions = new SpatialIndexOptions();
      spatialOptions.packing = packing;
      spatialOptions.validate();
      WriterOptions o = new WriterOptions();
      o.modelPaths.addAll(modelDirs);
      o.modelFiles.addAll(modelFiles);
      o.embedModels = embed;
      o.reverseIndex = !noReverseIndex;
      o.overwrite = overwrite;
      o.chunkSize = chunk;
      o.compression = compression;
      o.compressionLevel = level;
      o.numericEncoding = numeric;
      o.geometryEncoding = geometry;
      o.geometryCrs.putAll(geometryCrs);
      for (String order : spatialOrder) {
        int split = order.lastIndexOf('.');
        if (split < 1 || split == order.length() - 1)
          throw new IllegalArgumentException("Expected --spatial-order Class.Attribute");
        if (o.spatialOrder.put(order.substring(0, split), order.substring(split + 1)) != null)
          throw new IllegalArgumentException("Only one spatial ordering attribute per class");
      }
      ContainerWriter.create(input, output, o);
      for (String index : indexes) {
        String[] p = index.split(":", 2);
        if (p.length != 2) throw new IllegalArgumentException("Expected --spatial Class:Attribute");
        SpatialIndex.add(output, p[0], p[1], crs, spatialOptions);
      }
      return 0;
    }
  }

  public abstract static class ReadCommand {
    @Parameters(index = "0")
    String input;

    @Option(names = "--immutable-url")
    boolean immutable;

    @Option(names = "--allow-full-download")
    boolean full;

    protected IbxContainer open() throws IOException {
      if (input.startsWith("http://") || input.startsWith("https://")) {
        RemoteOptions o = new RemoteOptions();
        o.immutableUrl = immutable;
        o.allowFullDownload = full;
        return IbxContainer.open(URI.create(input), o);
      }
      return IbxContainer.open(Paths.get(input));
    }
  }

  @Command(name = "info", mixinStandardHelpOptions = true)
  public static final class Info extends ReadCommand implements Callable<Integer> {
    @Option(names = "--storage", description = "Physical bytes by section and directory entry type")
    boolean storage;

    public Integer call() throws Exception {
      try (IbxContainer c = open()) {
        Map<String, Object> info = new LinkedHashMap<String, Object>();
        info.put("formatVersion", c.metadata().formatVersion());
        info.put("geometryEncoding", c.metadata().geometryEncoding);
        info.put("geometryProfile", c.metadata().geometryProfile);
        info.put("geometries", c.metadata().geometries);
        info.put("transferVersion", c.metadata().version);
        info.put("bytes", c.size());
        info.put("models", c.metadata().models);
        info.put("topics", c.metadata().topics);
        info.put("classes", c.metadata().classes.keySet());
        info.put("numericEncoding", c.metadata().numericEncoding);
        info.put("spatialIndexes", SpatialIndex.manifest(c));
        info.put("spatialOrder", c.metadata().spatialOrder);
        if (storage)
          info.put("storage", ch.interlis.ibx.container.StorageDiagnostics.inspect(c));
        System.out.println(
            new com.fasterxml.jackson.databind.ObjectMapper()
                .writerWithDefaultPrettyPrinter()
                .writeValueAsString(info));
      }
      return 0;
    }
  }

  @Command(name = "export", mixinStandardHelpOptions = true)
  public static final class Export extends ReadCommand implements Callable<Integer> {
    @Parameters(index = "1")
    Path output;

    @Option(names = "--overwrite")
    boolean overwrite;

    public Integer call() throws Exception {
      try (IbxContainer c = open()) {
        writeFile(output, overwrite, out -> c.export(out));
      }
      return 0;
    }
  }

  interface Write {
    void write(OutputStream out) throws Exception;
  }

  static void writeFile(Path target, boolean overwrite, Write action) throws Exception {
    target = target.toAbsolutePath();
    if (Files.exists(target) && !overwrite) throw new FileAlreadyExistsException(target.toString());
    Files.createDirectories(target.getParent());
    Path temp = Files.createTempFile(target.getParent(), ".ibx-export-", ".tmp");
    try {
      try (OutputStream out = new BufferedOutputStream(Files.newOutputStream(temp))) {
        action.write(out);
      }
      FilesEx.publish(temp, target, overwrite);
    } finally {
      Files.deleteIfExists(temp);
    }
  }

  public abstract static class Selection extends ReadCommand implements Callable<Integer> {
    @Option(names = "--output")
    Path output;

    @Option(names = "--overwrite")
    boolean overwrite;

    abstract Fragment select(IbxContainer c) throws Exception;

    public Integer call() throws Exception {
      try (IbxContainer c = open();
          Fragment f = select(c)) {
        System.err.println("IBX fragment: " + f.description() + " (may be incomplete)");
        if (output != null) writeFile(output, overwrite, out -> c.exportFragment(f, out));
        else {
          c.exportFragment(f, System.out);
          System.out.flush();
        }
      }
      return 0;
    }
  }

  @Command(name = "get-topic", mixinStandardHelpOptions = true)
  public static final class GetTopic extends Selection {
    @Parameters(index = "1")
    String topic;

    Fragment select(IbxContainer c) {
      return c.getTopic(topic);
    }
  }

  @Command(name = "get-basket", mixinStandardHelpOptions = true)
  public static final class GetBasket extends Selection {
    @Parameters(index = "1")
    String bid;

    Fragment select(IbxContainer c) {
      return c.getBasket(bid);
    }
  }

  @Command(name = "get-class", mixinStandardHelpOptions = true)
  public static final class GetClass extends Selection {
    @Parameters(index = "1")
    String cls;

    Fragment select(IbxContainer c) {
      return c.getClass(cls);
    }
  }

  @Command(name = "get-object", mixinStandardHelpOptions = true)
  public static final class GetObject extends Selection {
    @Parameters(index = "1")
    String tid;

    Fragment select(IbxContainer c) {
      return c.getObject(tid);
    }
  }

  @Command(name = "bbox-candidates", mixinStandardHelpOptions = true)
  public static final class Bbox extends Selection {
    @Parameters(index = "1")
    String cls;

    @Parameters(index = "2")
    String attr;

    @Parameters(index = "3")
    double minX;

    @Parameters(index = "4")
    double minY;

    @Parameters(index = "5")
    double maxX;

    @Parameters(index = "6")
    double maxY;

    Fragment select(IbxContainer c) throws Exception {
      return c.querySpatialCandidates(cls, attr, new BoundingBox(minX, minY, maxX, maxY));
    }
  }

  @Command(name = "add-spatial-index", mixinStandardHelpOptions = true)
  public static final class Index implements Callable<Integer> {
    @Parameters(index = "0")
    Path input;

    @Parameters(index = "1")
    String cls;

    @Parameters(index = "2")
    String attr;

    @Option(names = "--spatial-packing", defaultValue = "str")
    String packing;

    @Option(names = "--crs")
    String crs;

    public Integer call() throws Exception {
      SpatialIndexOptions options = new SpatialIndexOptions();
      options.packing = packing;
      SpatialIndex.add(input, cls, attr, crs, options);
      return 0;
    }
  }
}
