package ch.interlis.ilicontainer;

import static org.junit.Assert.*;

import ch.ehi.basics.settings.Settings;
import ch.interlis.ilicontainer.api.*;
import ch.interlis.ilicontainer.container.*;
import ch.interlis.ilicontainer.iox.ModelBridge;
import ch.interlis.iom.IomObject;
import ch.interlis.iom_j.xtf.Xtf24Reader;
import ch.interlis.iox.*;
import ch.interlis.iox_j.logging.LogEventFactory;
import ch.interlis.iox_j.validator.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.junit.*;
import org.junit.rules.TemporaryFolder;

public class SemanticsTest {
  @Rule public TemporaryFolder tmp = new TemporaryFolder();

  WriterOptions options() {
    WriterOptions w = new WriterOptions();
    w.modelFiles.add(ContainerTest.fixture("Tiny.ili").toAbsolutePath().toString());
    return w;
  }

  @Test
  public void blackboxesAndOidlessAssociationsRoundtrip() throws Exception {
    String text = new String(Files.readAllBytes(ContainerTest.fixture("tiny.xtf")), "UTF-8");
    text =
        text.replace(
            "<Tiny:name>Grüezi</Tiny:name>",
            "<Tiny:name>Grüezi</Tiny:name><Tiny:xml><x:payload"
                + " xmlns:x=\"urn:example\"><x:value>hello &amp;"
                + " world</x:value></x:payload></Tiny:xml><Tiny:binary>AAEC/w==</Tiny:binary>");
    text =
        text.replace(
            "</Tiny:Data>\n<Tiny:Data ili:bid=\"b2\">",
            "<Tiny:Link><Tiny:a ili:ref=\"o1\"/><Tiny:b ili:ref=\"o2\"/></Tiny:Link></Tiny:Data>\n"
                + "<Tiny:Data ili:bid=\"b2\">");
    Path input = tmp.newFile("special.xtf").toPath();
    Files.write(input, text.getBytes("UTF-8"));
    Path file = tmp.getRoot().toPath().resolve("special.ilic");
    ContainerWriter.create(input, file, options());
    try (IliContainer c = IliContainer.open(file)) {
      try (Fragment f = c.getClass("Tiny.Data.Link")) {
        IomObject o = f.objects().findFirst().get().getObject();
        assertNull(o.getobjectoid());
        assertEquals("o1", o.getattrobj("a", 0).getobjectrefoid());
      }
      ByteArrayOutputStream out = new ByteArrayOutputStream();
      c.export(out);
      String result = out.toString("UTF-8");
      assertTrue(result, result.contains("urn:example"));
      assertTrue(result, result.contains("AAEC/w=="));
      assertTrue(result, result.contains("hello &amp; world"));
      Path exported = tmp.getRoot().toPath().resolve("special-roundtrip.xtf");
      Files.write(exported, out.toByteArray());
      Path verification = tmp.newFolder().toPath();
      ModelBridge bridge = ModelBridge.load(input, options(), verification);
      assertTrue(
          ch.interlis.ilicontainer.benchmark.RoundtripVerifier.verify(
                  input, exported, bridge, verification)
              > 0);
    }
  }

  @Test
  public void fullFixturesPassInterlisValidator() throws Exception {
    Path work = tmp.newFolder().toPath();
    ModelBridge bridge = ModelBridge.load(ContainerTest.fixture("tiny.xtf"), options(), work);
    List<String> errors = new ArrayList<String>();
    IoxLogging logging =
        event -> {
          if (event.getEventKind() == IoxLogEvent.ERROR) errors.add(event.getEventMsg());
        };
    ValidationConfig config = new ValidationConfig();
    LogEventFactory factory = new LogEventFactory(config);
    factory.setLogger(logging);
    Validator validator = new Validator(bridge.model, config, logging, factory, new Settings());
    Xtf24Reader reader = new Xtf24Reader(ContainerTest.fixture("tiny.xtf").toFile());
    reader.setModel(bridge.model);
    try {
      IoxEvent e;
      while ((e = reader.read()) != null) {
        validator.validate(e);
        if (e instanceof EndTransferEvent) break;
      }
    } finally {
      reader.close();
      validator.close();
    }
    assertTrue(errors.toString(), errors.isEmpty());
  }

  @Test
  public void emptyTransferAndOfflineFreshProcessExport() throws Exception {
    String text = new String(Files.readAllBytes(ContainerTest.fixture("tiny.xtf")), "UTF-8");
    int start = text.indexOf("<ili:datasection>") + "<ili:datasection>".length();
    text = text.substring(0, start) + text.substring(text.indexOf("</ili:datasection>"));
    Path input = tmp.newFile("empty.xtf").toPath();
    Files.write(input, text.getBytes("UTF-8"));
    Path file = tmp.getRoot().toPath().resolve("empty.ilic");
    ContainerWriter.create(input, file, options());
    Path populated = tmp.getRoot().toPath().resolve("populated.ilic");
    ContainerWriter.create(ContainerTest.fixture("tiny.xtf"), populated, options());
    for (Path source : Arrays.asList(file, populated)) {
      String java = Paths.get(System.getProperty("java.home"), "bin", "java").toString();
      Path out = tmp.getRoot().toPath().resolve(source.getFileName() + ".xtf"),
          log = tmp.getRoot().toPath().resolve("export.log");
      Process p =
          new ProcessBuilder(
                  java,
                  "-Dhttp.proxyHost=127.0.0.1",
                  "-Dhttp.proxyPort=9",
                  "-Dhttps.proxyHost=127.0.0.1",
                  "-Dhttps.proxyPort=9",
                  "-cp",
                  System.getProperty("ilic.test.classpath"),
                  "ch.interlis.ilicontainer.cli.Main",
                  "export",
                  source.toString(),
                  out.toString())
              .directory(tmp.getRoot())
              .redirectErrorStream(true)
              .redirectOutput(log.toFile())
              .start();
      assertTrue(p.waitFor(30, TimeUnit.SECONDS));
      assertEquals(new String(Files.readAllBytes(log), "UTF-8"), 0, p.exitValue());
      assertTrue(Files.size(out) > 0);
      if (source.equals(populated))
        assertTrue(new String(Files.readAllBytes(out), "UTF-8").contains("o1"));
    }
  }

  @Test
  public void growingTransferScansInFixedHeap() throws Exception {
    String text = new String(Files.readAllBytes(ContainerTest.fixture("tiny.xtf")), "UTF-8");
    String prefix =
        text.substring(0, text.indexOf("<ili:datasection>"))
            + "<ili:datasection><Tiny:Data ili:bid=\"many\">";
    Path input = tmp.newFile("many.xtf").toPath();
    try (BufferedWriter out = Files.newBufferedWriter(input)) {
      out.write(prefix);
      for (int i = 0; i < 100000; i++)
        out.write(
            "<Tiny:Item ili:tid=\"o"
                + i
                + "\"><Tiny:name>growing transfer</Tiny:name></Tiny:Item>");
      out.write("</Tiny:Data></ili:datasection></ili:transfer>");
    }
    Path file = tmp.getRoot().toPath().resolve("many.ilic");
    Path log = tmp.getRoot().toPath().resolve("scan.log");
    Process writer =
        new ProcessBuilder(
                Paths.get(System.getProperty("java.home"), "bin", "java").toString(),
                "-Xmx64m",
                "-cp",
                System.getProperty("ilic.test.classpath"),
                ScanProbe.class.getName(),
                input.toString(),
                file.toString(),
                ContainerTest.fixture("Tiny.ili").toAbsolutePath().toString())
            .redirectErrorStream(true)
            .redirectOutput(log.toFile())
            .start();
    assertTrue(writer.waitFor(60, TimeUnit.SECONDS));
    assertEquals(new String(Files.readAllBytes(log), "UTF-8"), 0, writer.exitValue());
    Process p =
        new ProcessBuilder(
                Paths.get(System.getProperty("java.home"), "bin", "java").toString(),
                "-Xmx32m",
                "-cp",
                System.getProperty("ilic.test.classpath"),
                ScanProbe.class.getName(),
                file.toString())
            .redirectErrorStream(true)
            .redirectOutput(log.toFile())
            .start();
    assertTrue(p.waitFor(45, TimeUnit.SECONDS));
    assertEquals(new String(Files.readAllBytes(log), "UTF-8"), 0, p.exitValue());
    assertTrue(new String(Files.readAllBytes(log), "UTF-8").contains("100000"));
  }

  @Test
  public void fragmentedInputStillProducesCompleteCoordinates() throws Exception {
    ModelBridge bridge =
        ModelBridge.load(ContainerTest.fixture("tiny.xtf"), options(), tmp.newFolder().toPath());
    assertEquals(
        Boolean.TRUE,
        javax.xml.stream.XMLInputFactory.newFactory()
            .getProperty(javax.xml.stream.XMLInputFactory.IS_COALESCING));
    for (final int block : new int[] {1, 3, 7, 64}) {
      try (InputStream raw = Files.newInputStream(ContainerTest.fixture("tiny.xtf"))) {
        InputStream fragmented =
            new FilterInputStream(raw) {
              public int read(byte[] b, int off, int len) throws IOException {
                return super.read(b, off, Math.min(len, block));
              }
            };
        Xtf24Reader reader = new Xtf24Reader(fragmented);
        reader.setModel(bridge.model);
        int count = 0;
        try {
          IoxEvent e;
          while ((e = reader.read()) != null) {
            if (e instanceof ObjectEvent) {
              IomObject o = ((ObjectEvent) e).getIomObject();
              if ("o2".equals(o.getobjectoid()))
                assertEquals("100.000", o.getattrobj("point", 0).getattrvalue("C2"));
              count++;
            }
            if (e instanceof EndTransferEvent) break;
          }
        } finally {
          reader.close();
        }
        assertEquals(3, count);
      }
    }
  }
}
