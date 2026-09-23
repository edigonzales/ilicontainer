package ch.interlis.ibx;

import static org.junit.Assert.*;

import ch.interlis.ibx.api.*;
import ch.interlis.ibx.benchmark.RoundtripVerifier;
import ch.interlis.ibx.bridge.BridgeMain;
import ch.interlis.ibx.container.*;
import ch.interlis.ibx.navigation.Navigation;
import com.fasterxml.jackson.databind.*;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import org.junit.*;
import org.junit.rules.TemporaryFolder;

public class NavigationTest {
  @Rule public TemporaryFolder temp = new TemporaryFolder();

  static WriterOptions options(boolean reverse) {
    WriterOptions o = new WriterOptions();
    o.geometryEncoding = "wkb";
    o.reverseIndex = reverse;
    o.chunkSize = 1;
    o.modelFiles.add(Paths.get("demo/Quartier.ili").toAbsolutePath().toString());
    for (String key :
        Arrays.asList(
            "Gebaeude.Grundriss",
            "Gebaeude.Beschriftung",
            "Anlage.Position",
            "Spielplatz.Position",
            "Technik.Position",
            "Kontrolle.Standort")) o.geometryCrs.put("Quartier.Unterhalt." + key, "EPSG:2056");
    return o;
  }

  private Path create(boolean reverse) throws Exception {
    Path p = temp.getRoot().toPath().resolve("demo" + reverse + ".ibx");
    ContainerWriter.create(Paths.get("demo/quartier.xtf"), p, options(reverse));
    return p;
  }

  @Test
  public void demoValidatesAndRoundtripsIndependently() throws Exception {
    Path input = Paths.get("demo/quartier.xtf");
    Path work = temp.newFolder().toPath();
    ch.interlis.ibx.iox.ModelBridge model =
        ch.interlis.ibx.iox.ModelBridge.load(input, options(true), work);
    java.util.List<String> errors = new java.util.ArrayList<String>();
    ch.interlis.iox.IoxLogging logging =
        e -> {
          if (e.getEventKind() == ch.interlis.iox.IoxLogEvent.ERROR) errors.add(e.getEventMsg());
        };
    ch.interlis.iox_j.validator.ValidationConfig config =
        new ch.interlis.iox_j.validator.ValidationConfig();
    ch.interlis.iox_j.logging.LogEventFactory factory =
        new ch.interlis.iox_j.logging.LogEventFactory(config);
    factory.setLogger(logging);
    ch.interlis.iox_j.validator.Validator validator =
        new ch.interlis.iox_j.validator.Validator(
            model.model, config, logging, factory, new ch.ehi.basics.settings.Settings());
    ch.interlis.iom_j.xtf.Xtf24Reader reader =
        new ch.interlis.iom_j.xtf.Xtf24Reader(input.toFile());
    reader.setModel(model.model);
    try {
      ch.interlis.iox.IoxEvent e;
      while ((e = reader.read()) != null) {
        validator.validate(e);
        if (e instanceof ch.interlis.iox.EndTransferEvent) break;
      }
    } finally {
      reader.close();
      validator.close();
    }
    assertTrue(errors.toString(), errors.isEmpty());
    Path output = temp.getRoot().toPath().resolve("roundtrip.xtf");
    try (IbxContainer c = IbxContainer.open(create(true));
        OutputStream out = Files.newOutputStream(output)) {
      c.export(out);
    }
    assertTrue(RoundtripVerifier.verify(input, output, model, work) > 0);
  }

  @Test
  public void catalogAndNavigationDoNotScanObjects() throws Exception {
    Path file = create(true);
    RemoteOptions o = new RemoteOptions();
    o.prefetchPositions = 0;
    try (IbxContainer c = IbxContainer.open(file, o)) {
      Navigation n = new Navigation(c);
      n.describe();
      Map<String, Object> page = n.catalog(null, 256);
      assertEquals(7, ((List<?>) page.get("items")).size());
      assertEquals(0, c.metrics().chunksRead);
      Map<String, Object> target = n.resolve("auftrag0", null);
      long fid = ((Number) target.get("fid")).longValue();
      assertEquals(1, c.metrics().chunksRead);
      Set<Long> sources = new HashSet<Long>();
      String after = null;
      int count = 0;
      do {
        Map<String, Object> related = n.related(fid, after, 2);
        for (Object v : (List<?>) related.get("items")) {
          Map<?, ?> edge = (Map<?, ?>) v;
          assertTrue(sources.add(((Number) edge.get("sourceFid")).longValue()));
          count++;
        }
        after = (String) related.get("next");
      } while (after != null);
      assertEquals(7, count);
      assertTrue(c.metrics().chunksRead <= 8);
      Map<String, Object> building = n.resolve("g0", null);
      assertEquals("nord", building.get("bid"));
      Map<String, Object> fields = (Map<String, Object>) building.get("fields");
      assertEquals(2, ((List<?>) fields.get("Kontrollen")).size());
      assertEquals(
          "Gebäude", c.metadata().definitions.get("Quartier.Unterhalt.Gebaeude").get("label"));
      assertEquals(
          "Quartier.Unterhalt.Auftrag",
          c.metadata().definitions.get("Quartier.Unterhalt.Gebaeude.Auftrag").get("target"));
      assertNotNull(n.resolve("org0", null));
      assertNull(n.resolve("org0", "wrong-basket"));
      assertNull(n.resolve("missing", null));
    }
  }

  @Test
  public void missingTargetStaysAReferenceAndDoesNotCreateAnIncomingEdge() throws Exception {
    Path input = temp.getRoot().toPath().resolve("missing-target.xtf");
    String source = new String(Files.readAllBytes(Paths.get("demo/quartier.xtf")), "UTF-8");
    source = source.replaceFirst("ili:ref=\"auftrag0\"", "ili:ref=\"missing-target\"");
    Files.write(input, source.getBytes("UTF-8"));
    Path file = temp.getRoot().toPath().resolve("missing-target.ibx");
    ContainerWriter.create(input, file, options(true));
    try (IbxContainer c = IbxContainer.open(file)) {
      Navigation n = new Navigation(c);
      Map<?, ?> fields = (Map<?, ?>) n.resolve("g0", null).get("fields");
      Map<?, ?> ref = (Map<?, ?>) ((List<?>) fields.get("Auftrag")).get(0);
      assertEquals("missing-target", ref.get("tid"));
      assertNull(n.resolve("missing-target", null));
      long fid = ((Number) n.resolve("auftrag0", null).get("fid")).longValue();
      assertEquals(6, ((List<?>) n.related(fid, null, 50).get("items")).size());
    }
  }

  @Test
  public void reverseIndexAbsentIsNotAnEmptyRelationship() throws Exception {
    try (IbxContainer c = IbxContainer.open(create(false))) {
      assertEquals(false, new Navigation(c).related(0, null, 50).get("indexed"));
    }
  }

  @Test
  public void structureReferencesAndOidlessAssociationsAreAddressable() throws Exception {
    try (IbxContainer c = IbxContainer.open(create(true))) {
      Navigation n = new Navigation(c);
      Map<String, Object> org = n.resolve("org0", null);
      Map<String, Object> related = n.related(((Number) org.get("fid")).longValue(), null, 256);
      boolean structure = false, association = false;
      for (Object item : (List<?>) related.get("items")) {
        Map<?, ?> edge = (Map<?, ?>) item;
        Map<?, ?> object = (Map<?, ?>) edge.get("object");
        if (edge.get("path").toString().contains("/Kontrollen/")) structure = true;
        if (object.get("className").toString().endsWith("Zustaendigkeit")) {
          association = true;
          assertNull(object.get("tid"));
          assertTrue(((Map<?, ?>) object.get("fields")).containsKey("Funktion"));
        }
      }
      assertTrue(structure);
      assertTrue(association);
    }
  }

  @Test
  public void bridgePagesExportAndRejectsMissingAuthentication() throws Exception {
    Path file = create(true);
    byte[] before = Files.readAllBytes(file);
    ObjectMapper json = new ObjectMapper();
    try (BridgeMain bridge = new BridgeMain()) {
      URL url = new URL("http://127.0.0.1:" + bridge.port() + "/v1");
      HttpURLConnection denied = (HttpURLConnection) url.openConnection();
      denied.setRequestMethod("POST");
      assertEquals(403, denied.getResponseCode());
      denied.disconnect();
      JsonNode opened = call(bridge, Navigation.map("op", "open", "source", file.toString()));
      String session = opened.get("session").asText();
      JsonNode initialActivity =
          call(bridge, Navigation.map("op", "activity", "session", session));
      assertEquals(1, initialActivity.get("events").size());
      assertEquals("open", initialActivity.get("events").get(0).get("op").asText());
      assertEquals("success", initialActivity.get("events").get(0).get("state").asText());
      assertTrue(initialActivity.get("totals").get("bytesRead").asLong() > 0);
      JsonNode page =
          call(
              bridge,
              Navigation.map(
                  "op",
                  "query",
                  "session",
                  session,
                  "className",
                  "Quartier.Unterhalt.Gebaeude",
                  "geometry",
                  "Grundriss",
                  "limit",
                  5));
      JsonNode firstActivity = call(bridge, Navigation.map("op", "activity", "session", session));
      assertEquals(2, firstActivity.get("events").size());
      assertEquals("query", firstActivity.get("events").get(1).get("op").asText());
      assertEquals("success", firstActivity.get("events").get(1).get("state").asText());
      assertEquals(5, firstActivity.get("events").get(1).get("resultCount").asInt());
      assertEquals(
          call(bridge, Navigation.map("op", "metrics", "session", session))
              .get("bytesRead")
              .asLong(),
          firstActivity.get("totals").get("bytesRead").asLong());
      assertEquals(
          2,
          call(bridge, Navigation.map("op", "activity", "session", session))
              .get("events")
              .size()); // Polling is deliberately absent from its own activity history.

      // The activity endpoint must remain responsive while regular session access is locked.
      java.lang.reflect.Field sessionsField = BridgeMain.class.getDeclaredField("sessions");
      sessionsField.setAccessible(true);
      Object sessionState = ((Map<?, ?>) sessionsField.get(bridge)).get(session);
      ExecutorService poller = Executors.newSingleThreadExecutor();
      try {
        synchronized (sessionState) {
          Future<JsonNode> snapshot =
              poller.submit(
                  () -> call(bridge, Navigation.map("op", "activity", "session", session)));
          assertEquals(2, snapshot.get(2, TimeUnit.SECONDS).get("events").size());
        }
      } finally {
        poller.shutdownNow();
      }
      assertEquals(
          400,
          callAllowFailure(
                  bridge,
                  Navigation.map("op", "notAnOperation", "session", session))
              .get("status"));
      JsonNode afterFailure = call(bridge, Navigation.map("op", "activity", "session", session));
      assertEquals("failed", afterFailure.get("events").get(2).get("state").asText());
      assertEquals(
          "Unknown protocol operation",
          afterFailure.get("events").get(2).get("error").asText());
      Set<Long> fids = new TreeSet<Long>();
      while (true) {
        for (JsonNode item : page.get("items")) {
          assertTrue(fids.add(item.get("fid").asLong()));
          assertTrue(item.hasNonNull("wkb"));
        }
        if (page.get("cursor").isNull()) break;
        page =
            call(
                bridge,
                Navigation.map(
                    "op",
                    "next",
                    "session",
                    session,
                    "cursor",
                    page.get("cursor").asText(),
                    "limit",
                    5));
      }
      assertEquals(24, fids.size());
      Path target = temp.getRoot().toPath().resolve("fragment.xtf");
      List<Long> selected = Arrays.asList(fids.iterator().next(), fids.iterator().next());
      JsonNode exported =
          call(
              bridge,
              Navigation.map(
                  "op",
                  "export",
                  "session",
                  session,
                  "fids",
                  selected,
                  "target",
                  target.toString()));
      assertEquals(1, exported.get("count").asInt());
      String text = new String(Files.readAllBytes(target), "UTF-8");
      assertTrue(text.contains("fragment"));
      assertTrue(text.contains("Kontrollen"));
      assertTrue(text.contains("Grundriss"));
      assertTrue(text.contains("Beschriftung"));
      assertArrayEquals(before, Files.readAllBytes(file));
      for (int i = 0; i < 205; i++)
        call(bridge, Navigation.map("op", "describe", "session", session));
      JsonNode bounded = call(bridge, Navigation.map("op", "activity", "session", session));
      assertEquals(200, bounded.get("events").size());
      assertEquals(
          call(bridge, Navigation.map("op", "metrics", "session", session))
              .get("bytesRead")
              .asLong(),
          bounded.get("totals").get("bytesRead").asLong());
      call(bridge, Navigation.map("op", "close", "session", session));
    }
  }

  private JsonNode call(BridgeMain bridge, Map<String, Object> q) throws Exception {
    ObjectMapper json = new ObjectMapper();
    HttpURLConnection c =
        (HttpURLConnection) new URL("http://127.0.0.1:" + bridge.port() + "/v1").openConnection();
    c.setRequestMethod("POST");
    c.setDoOutput(true);
    c.setRequestProperty("X-IBX-Token", bridge.token());
    try {
      try (OutputStream out = c.getOutputStream()) {
        out.write(json.writeValueAsBytes(q));
      }
      assertEquals(200, c.getResponseCode());
      try (InputStream in = c.getInputStream()) {
        return json.readTree(in);
      }
    } finally {
      c.disconnect();
    }
  }

  private Map<String, Object> callAllowFailure(BridgeMain bridge, Map<String, Object> q)
      throws Exception {
    ObjectMapper json = new ObjectMapper();
    HttpURLConnection c =
        (HttpURLConnection)
            new URL("http://127.0.0.1:" + bridge.port() + "/v1").openConnection();
    c.setRequestMethod("POST");
    c.setDoOutput(true);
    c.setRequestProperty("X-IBX-Token", bridge.token());
    try {
      try (OutputStream out = c.getOutputStream()) {
        out.write(json.writeValueAsBytes(q));
      }
      int status = c.getResponseCode();
      InputStream stream = status >= 400 ? c.getErrorStream() : c.getInputStream();
      try (InputStream in = stream) {
        return Navigation.map("status", status, "body", json.readTree(in));
      }
    } finally {
      c.disconnect();
    }
  }
}
