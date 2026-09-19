package ch.interlis.ibx;

import static org.junit.Assert.*;

import ch.interlis.ibx.api.*;
import ch.interlis.ibx.benchmark.RangeServer;
import ch.interlis.ibx.container.*;
import java.io.*;
import java.nio.file.*;
import org.junit.*;
import org.junit.rules.TemporaryFolder;

@org.junit.runner.RunWith(org.junit.runners.Parameterized.class)
public class RemoteTest {
  @org.junit.runners.Parameterized.Parameters(name = "geometry={0}")
  public static java.util.Collection<Object[]> encodings() {
    return java.util.Arrays.asList(new Object[][] {{"iom"}, {"wkb"}});
  }

  @org.junit.runners.Parameterized.Parameter public String geometryEncoding;

  private void geometryOptions(WriterOptions w) {
    w.geometryEncoding = geometryEncoding;
    w.geometryCrs.put("Tiny.Data.Item.point", "EPSG:2056");
    w.geometryCrs.put("Tiny.Data.Item.line", "EPSG:2056");
  }

  @Rule public TemporaryFolder tmp = new TemporaryFolder();

  Path create() throws Exception {
    WriterOptions o = new WriterOptions();
    geometryOptions(o);
    o.modelFiles.add(ContainerTest.fixture("Tiny.ili").toString());
    Path target = tmp.getRoot().toPath().resolve("data.ibx");
    ContainerWriter.create(ContainerTest.fixture("tiny.xtf"), target, o);
    return target;
  }

  @Test
  public void rangeReadAndChangedSnapshot() throws Exception {
    Path p = create();
    try (RangeServer server = new RangeServer(p);
        IbxContainer c = IbxContainer.open(server.uri())) {
      try (Fragment f = c.getObject("o1")) {
        assertEquals("Grüezi", f.objects().findFirst().get().getObject().getattrvalue("name"));
      }
      assertTrue(server.requests > 1);
      c.clearCache();
      server.mode = "changed";
      try (Fragment f = c.getObject("o2")) {
        f.objects().count();
        fail("mixed snapshot accepted");
      } catch (UncheckedIOException expected) {
        assertTrue(expected.getMessage().contains("changed"));
      }
    }
  }

  @Test
  public void rangeRejectionAndExplicitDownload() throws Exception {
    Path p = create();
    try (RangeServer server = new RangeServer(p)) {
      server.mode = "full";
      try {
        IbxContainer.open(server.uri());
        fail();
      } catch (IOException expected) {
      }
      RemoteOptions o = new RemoteOptions();
      o.allowFullDownload = true;
      try (IbxContainer c = IbxContainer.open(server.uri(), o);
          Fragment f = c.getObject("o3")) {
        assertEquals(1, f.objects().count());
      }
      server.mode = "no-etag";
      try {
        IbxContainer.open(server.uri());
        fail();
      } catch (IOException expected) {
      }
      o = new RemoteOptions();
      o.immutableUrl = true;
      try (IbxContainer c = IbxContainer.open(server.uri(), o);
          Fragment f = c.getBasket("b1")) {
        assertEquals(2, f.objects().count());
      }
      server.mode = "bad-range";
      try {
        IbxContainer.open(server.uri());
        fail();
      } catch (IOException expected) {
      }
    }
  }

  @Test
  public void changedRemoteExportNeverReplacesTarget() throws Exception {
    Path input = tmp.newFile("large.xtf").toPath(),
        source = tmp.getRoot().toPath().resolve("large.ibx");
    String text = new String(Files.readAllBytes(ContainerTest.fixture("tiny.xtf")), "UTF-8");
    text = text.replace("Grüezi", String.join("", java.util.Collections.nCopies(100000, "abc")));
    Files.write(input, text.getBytes("UTF-8"));
    WriterOptions options = new WriterOptions();
    geometryOptions(options);
    options.modelFiles.add(ContainerTest.fixture("Tiny.ili").toString());
    options.compression = "none";
    ContainerWriter.create(input, source, options);
    assertTrue(Files.size(source) > 65536);
    Path output = tmp.newFile("existing.xtf").toPath();
    byte[] original = "existing caller content".getBytes("UTF-8");
    Files.write(output, original);
    try (RangeServer server = new RangeServer(source)) {
      server.changeAfterRequests = 6;
      int status =
          ch.interlis.ibx.cli.Main.execute(
              "export", server.uri().toString(), output.toString(), "--overwrite");
      assertNotEquals(0, status);
      assertArrayEquals(original, Files.readAllBytes(output));
      try (java.util.stream.Stream<Path> files = Files.list(tmp.getRoot().toPath())) {
        assertFalse(files.anyMatch(p -> p.getFileName().toString().startsWith(".ibx-export-")));
      }
    }
  }
}
