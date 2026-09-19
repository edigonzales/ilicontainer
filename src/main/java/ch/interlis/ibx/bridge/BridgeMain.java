package ch.interlis.ibx.bridge;

import static ch.interlis.ibx.navigation.Navigation.map;

import ch.interlis.ibx.api.*;
import ch.interlis.ibx.container.*;
import ch.interlis.ibx.navigation.Navigation;
import com.fasterxml.jackson.databind.*;
import com.sun.net.httpserver.*;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Private loopback transport, launched and owned by QGIS. No unauthenticated endpoints. */
public final class BridgeMain implements AutoCloseable {
  private static final ObjectMapper JSON = new ObjectMapper();
  private final String token = UUID.randomUUID().toString() + UUID.randomUUID();
  private final HttpServer server;
  private final ExecutorService workers = Executors.newFixedThreadPool(8);
  private final ScheduledExecutorService reaper = Executors.newSingleThreadScheduledExecutor();
  private final ConcurrentMap<String, Session> sessions = new ConcurrentHashMap<String, Session>();
  private final ConcurrentMap<String, AtomicBoolean> cancelled =
      new ConcurrentHashMap<String, AtomicBoolean>();

  private static final class Cursor {
    final ch.interlis.ibx.container.CloseableIterator<Map<String, Object>> source;
    final String geometry;
    final Set<String> fields;
    final boolean noGeometry;
    long accessed = System.currentTimeMillis();

    Cursor(ch.interlis.ibx.container.CloseableIterator<Map<String, Object>> s, JsonNode q) {
      source = s;
      geometry = text(q, "geometry");
      fields = q.has("fields") ? strings(q.get("fields")) : null;
      noGeometry = q.path("noGeometry").asBoolean();
    }
  }

  private static final class Session implements AutoCloseable {
    final IbxContainer container;
    final Navigation navigation;
    final String source;
    final Map<String, Cursor> cursors = new HashMap<String, Cursor>();

    Session(IbxContainer c, String source) {
      container = c;
      navigation = new Navigation(c);
      this.source = source;
    }

    public synchronized void close() throws IOException {
      for (Cursor c : cursors.values()) c.source.close();
      cursors.clear();
      container.close();
    }
  }

  public BridgeMain() throws IOException {
    server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
    server.setExecutor(workers);
    server.createContext("/v1", this::handle);
    server.start();
    reaper.scheduleAtFixedRate(
        () -> {
          for (Session s : sessions.values())
            synchronized (s) {
              Iterator<Cursor> it = s.cursors.values().iterator();
              while (it.hasNext()) {
                Cursor c = it.next();
                if (System.currentTimeMillis() - c.accessed > 60000) {
                  try {
                    c.source.close();
                  } catch (IOException ignored) {
                  }
                  it.remove();
                }
              }
            }
        },
        30,
        30,
        TimeUnit.SECONDS);
  }

  public int port() {
    return server.getAddress().getPort();
  }

  public String token() {
    return token;
  }

  private void handle(HttpExchange exchange) throws IOException {
    int status = 200;
    Object result;
    try {
      if (!"POST".equals(exchange.getRequestMethod())
          || !token.equals(exchange.getRequestHeaders().getFirst("X-IBX-Token"))) {
        status = 403;
        result = map("error", "Forbidden");
      } else {
        ByteArrayOutputStream body = new ByteArrayOutputStream();
        byte[] b = new byte[8192];
        int n;
        try (InputStream in = exchange.getRequestBody()) {
          while ((n = in.read(b)) != -1) {
            if (body.size() + n > 4 * 1024 * 1024) throw new IOException("Request too large");
            body.write(b, 0, n);
          }
        }
        JsonNode q = JSON.readTree(body.toByteArray());
        result = dispatch(q);
      }
    } catch (Exception e) {
      status = 400;
      Throwable cause = e instanceof UncheckedIOException ? e.getCause() : e;
      result =
          map(
              "error",
              cause.getMessage() == null ? cause.getClass().getSimpleName() : cause.getMessage(),
              "code",
              cause.getClass().getSimpleName());
    }
    byte[] bytes = JSON.writeValueAsBytes(result);
    exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
    exchange.sendResponseHeaders(status, bytes.length);
    try (OutputStream out = exchange.getResponseBody()) {
      out.write(bytes);
    } finally {
      exchange.close();
    }
  }

  private Object dispatch(JsonNode q) throws Exception {
    String op = q.path("op").asText(), request = text(q, "requestId");
    if (op.equals("cancel")) {
      AtomicBoolean flag = cancelled.get(q.path("target").asText());
      if (flag != null) flag.set(true);
      return map("ok", true);
    }
    AtomicBoolean flag = new AtomicBoolean();
    if (request != null) cancelled.put(request, flag);
    try {
      if (op.equals("open")) {
        String source = q.path("source").asText();
        RemoteOptions options = new RemoteOptions();
        options.connectTimeoutMillis = 5000;
        options.readTimeoutMillis = 10000;
        options.allowFullDownload = q.path("allowFullDownload").asBoolean();
        options.immutableUrl = q.path("immutableUrl").asBoolean();
        IbxContainer c =
            source.startsWith("https://") || source.startsWith("http://")
                ? IbxContainer.open(URI.create(source), options)
                : IbxContainer.open(Paths.get(source), options);
        if (flag.get()) {
          c.close();
          throw new IOException("Cancelled");
        }
        String id = UUID.randomUUID().toString();
        Session s = new Session(c, source);
        sessions.put(id, s);
        return map("session", id, "state", c.state(), "description", s.navigation.describe());
      }
      String id = q.path("session").asText();
      Session s = sessions.get(id);
      if (s == null) throw new IOException("Session closed; reopen source");
      synchronized (s) {
        if (flag.get()) throw new IOException("Cancelled");
        switch (op) {
          case "close":
            sessions.remove(id);
            s.close();
            return map("ok", true);
          case "describe":
            return s.navigation.describe();
          case "baskets":
            return s.navigation.baskets(text(q, "after"), q.path("limit").asInt(256));
          case "catalog":
            return s.navigation.catalog(text(q, "after"), q.path("limit").asInt(256));
          case "metrics":
            return s.container.metrics();
          case "object":
            return q.has("fid")
                ? s.navigation.object(q.get("fid").asLong())
                : s.navigation.resolve(q.path("tid").asText(), text(q, "bid"));
          case "related":
            return s.navigation.related(
                q.path("fid").asLong(), text(q, "after"), q.path("limit").asInt(50));
          case "query":
            {
              if (s.cursors.size() >= 128) throw new IOException("Too many open iterators");
              ch.interlis.ibx.container.CloseableIterator<Map<String, Object>> source;
              if (q.has("fids")) {
                List<Long> fids = new ArrayList<Long>();
                for (JsonNode f : q.get("fids")) fids.add(f.asLong());
                Iterator<Long> it = new TreeSet<Long>(fids).iterator();
                source =
                    new CloseableIterator<Map<String, Object>>() {
                      Map<String, Object> next;

                      public boolean hasNext() {
                        try {
                          while (next == null && it.hasNext()) {
                            Map<String, Object> o = s.navigation.object(it.next());
                            if (o != null
                                && q.path("className").asText().equals(o.get("className"))
                                && (strings(q.get("bids")).isEmpty()
                                    || strings(q.get("bids")).contains(o.get("bid")))) next = o;
                          }
                          return next != null;
                        } catch (IOException e) {
                          throw new UncheckedIOException(e);
                        }
                      }

                      public Map<String, Object> next() {
                        if (!hasNext()) throw new NoSuchElementException();
                        Map<String, Object> o = next;
                        next = null;
                        return o;
                      }

                      public void close() {}
                    };
              } else {
                BoundingBox box =
                    q.hasNonNull("bbox")
                        ? JSON.treeToValue(q.get("bbox"), BoundingBox.class)
                        : null;
                source =
                    s.navigation.query(
                        q.path("className").asText(),
                        text(q, "geometry"),
                        box,
                        strings(q.get("bids")));
              }
              String cid = UUID.randomUUID().toString();
              s.cursors.put(cid, new Cursor(source, q));
              return page(s, cid, q.path("limit").asInt(256), flag);
            }
          case "next":
            return page(s, q.path("cursor").asText(), q.path("limit").asInt(256), flag);
          case "closeCursor":
            {
              Cursor c = s.cursors.remove(q.path("cursor").asText());
              if (c != null) c.source.close();
              return map("ok", true);
            }
          case "export":
            return export(s, q, flag);
          default:
            throw new IOException("Unknown protocol operation");
        }
      }
    } finally {
      if (request != null) cancelled.remove(request);
    }
  }

  private Object page(Session s, String id, int limit, AtomicBoolean cancel) throws IOException {
    if (limit < 1 || limit > 256) throw new IOException("Page size must be 1..256");
    Cursor c = s.cursors.get(id);
    if (c == null) throw new IOException("Iterator expired; repeat query");
    c.accessed = System.currentTimeMillis();
    List<Object> items = new ArrayList<Object>();
    try {
      while (items.size() < limit && c.source.hasNext()) {
        if (cancel.get()) throw new IOException("Cancelled");
        Map<String, Object> object = c.source.next();
        Map<String, Object> attrs = new LinkedHashMap<String, Object>();
        String wkb = null;
        Map<String, List<Map<String, Object>>> fields = (Map) object.get("fields");
        for (Map.Entry<String, List<Map<String, Object>>> entry : fields.entrySet()) {
          if (entry.getKey().equals(c.geometry)) {
            if (!entry.getValue().isEmpty()) wkb = (String) entry.getValue().get(0).get("wkb");
            continue;
          }
          if (c.fields != null && !c.fields.contains(entry.getKey())) continue;
          List<Map<String, Object>> vs = entry.getValue();
          if (vs.size() == 1 && "geometry".equals(vs.get(0).get("kind"))) continue;
          if (vs.size() == 1 && "scalar".equals(vs.get(0).get("kind")))
            attrs.put(entry.getKey(), vs.get(0).get("value"));
          else attrs.put(entry.getKey(), map("items", vs));
        }
        items.add(
            map(
                "fid",
                object.get("fid"),
                "tid",
                object.get("tid"),
                "bid",
                object.get("bid"),
                "attributes",
                attrs,
                "wkb",
                c.noGeometry ? null : wkb));
      }
      boolean more = c.source.hasNext();
      if (!more) {
        c.source.close();
        s.cursors.remove(id);
      }
      return map("items", items, "cursor", more ? id : null);
    } catch (Exception ex) {
      c.source.close();
      s.cursors.remove(id);
      throw ex;
    }
  }

  private Object export(Session s, JsonNode q, AtomicBoolean cancel) throws Exception {
    TreeSet<Long> fids = new TreeSet<Long>();
    for (JsonNode f : q.path("fids")) fids.add(f.asLong());
    if (fids.isEmpty() || fids.size() > 20000)
      throw new IOException("Select 1..20000 original objects");
    List<Location> locations = new ArrayList<Location>();
    for (long fid : fids)
      try (Fragment f = s.container.getFid(fid);
          CloseableIterator<Location> it = f.locations()) {
        if (it.hasNext()) locations.add(it.next());
        else throw new IOException("Unknown selected object " + fid);
      }
    Path target = Paths.get(q.path("target").asText()).toAbsolutePath();
    if (Files.exists(target))
      throw new IOException("Export target already exists; choose a new file");
    Path tmp = Files.createTempFile(target.getParent(), ".ibx-export-", ".xtf");
    try {
      try (Fragment f =
              new Fragment(
                  s.container,
                  () ->
                      new CloseableIterator<Location>() {
                        Iterator<Location> it = locations.iterator();

                        public boolean hasNext() {
                          if (cancel.get()) throw new IllegalStateException("Cancelled");
                          return it.hasNext();
                        }

                        public Location next() {
                          return it.next();
                        }

                        public void close() {}
                      },
                  "selected original objects");
          OutputStream out = Files.newOutputStream(tmp)) {
        s.container.exportFragment(f, out);
      }
      if (cancel.get()) throw new IOException("Cancelled");
      FilesEx.publish(tmp, target, false);
      return map("count", fids.size(), "target", target.toString());
    } finally {
      Files.deleteIfExists(tmp);
    }
  }

  private static Set<String> strings(JsonNode node) {
    Set<String> s = new LinkedHashSet<String>();
    if (node != null) for (JsonNode n : node) s.add(n.asText());
    return s;
  }

  private static String text(JsonNode q, String name) {
    return q.hasNonNull(name) ? q.get(name).asText() : null;
  }

  public void close() {
    server.stop(0);
    reaper.shutdownNow();
    for (Session s : sessions.values())
      try {
        s.close();
      } catch (IOException ignored) {
      }
    sessions.clear();
    workers.shutdownNow();
  }

  public static void main(String[] args) throws Exception {
    if (Integer.parseInt(System.getProperty("java.specification.version")) < 21)
      throw new IllegalStateException("IBX requires Java 21 or newer");
    final BridgeMain bridge = new BridgeMain();
    Runtime.getRuntime().addShutdownHook(new Thread(bridge::close));
    System.out.println(
        JSON.writeValueAsString(
            map("protocol", 1, "port", bridge.port(), "token", bridge.token())));
    System.out.flush();
    while (System.in.read() != -1) {}
    bridge.close();
  }
}
