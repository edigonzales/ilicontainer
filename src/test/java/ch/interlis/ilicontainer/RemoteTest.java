package ch.interlis.ilicontainer;

import static org.junit.Assert.*;

import ch.interlis.ilicontainer.api.*;
import ch.interlis.ilicontainer.benchmark.RangeServer;
import ch.interlis.ilicontainer.container.*;
import java.io.*;
import java.nio.file.*;
import org.junit.*;
import org.junit.rules.TemporaryFolder;

public class RemoteTest {
  @Rule public TemporaryFolder tmp = new TemporaryFolder();

  Path create() throws Exception {
    WriterOptions o = new WriterOptions();
    o.modelFiles.add(ContainerTest.fixture("Tiny.ili").toString());
    Path target = tmp.getRoot().toPath().resolve("data.ilic");
    ContainerWriter.create(ContainerTest.fixture("tiny.xtf"), target, o);
    return target;
  }

  @Test
  public void rangeReadAndChangedSnapshot() throws Exception {
    Path p = create();
    try (RangeServer server = new RangeServer(p);
        IliContainer c = IliContainer.open(server.uri())) {
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
        IliContainer.open(server.uri());
        fail();
      } catch (IOException expected) {
      }
      RemoteOptions o = new RemoteOptions();
      o.allowFullDownload = true;
      try (IliContainer c = IliContainer.open(server.uri(), o);
          Fragment f = c.getObject("o3")) {
        assertEquals(1, f.objects().count());
      }
      server.mode = "no-etag";
      try {
        IliContainer.open(server.uri());
        fail();
      } catch (IOException expected) {
      }
      o = new RemoteOptions();
      o.immutableUrl = true;
      try (IliContainer c = IliContainer.open(server.uri(), o);
          Fragment f = c.getBasket("b1")) {
        assertEquals(2, f.objects().count());
      }
      server.mode = "bad-range";
      try {
        IliContainer.open(server.uri());
        fail();
      } catch (IOException expected) {
      }
    }
  }

  @Test
  public void changedRemoteExportNeverReplacesTarget() throws Exception {
    Path input = tmp.newFile("large.xtf").toPath(),
        source = tmp.getRoot().toPath().resolve("large.ilic");
    String text = new String(Files.readAllBytes(ContainerTest.fixture("tiny.xtf")), "UTF-8");
    text = text.replace("Grüezi", String.join("", java.util.Collections.nCopies(100000, "abc")));
    Files.write(input, text.getBytes("UTF-8"));
    WriterOptions options = new WriterOptions();
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
          ch.interlis.ilicontainer.cli.Main.execute(
              "export", server.uri().toString(), output.toString(), "--overwrite");
      assertNotEquals(0, status);
      assertArrayEquals(original, Files.readAllBytes(output));
      try (java.util.stream.Stream<Path> files = Files.list(tmp.getRoot().toPath())) {
        assertFalse(files.anyMatch(p -> p.getFileName().toString().startsWith(".ilic-export-")));
      }
    }
  }
}
