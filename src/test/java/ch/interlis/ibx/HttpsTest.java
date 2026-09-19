package ch.interlis.ibx;

import static org.junit.Assert.*;

import ch.interlis.ibx.api.*;
import ch.interlis.ibx.container.*;
import com.sun.net.httpserver.*;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.security.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import javax.net.ssl.*;
import org.junit.*;
import org.junit.rules.TemporaryFolder;

/** Real TLS, test-local trust store, never disables certificate/hostname validation. */
public class HttpsTest {
  @Rule public TemporaryFolder temp = new TemporaryFolder();

  @Test
  public void tlsRangesRedirectsConsistencyAndFailures() throws Exception {
    Path store = temp.getRoot().toPath().resolve("server.p12");
    Process keytool =
        new ProcessBuilder(
                Paths.get(System.getProperty("java.home"), "bin", "keytool").toString(),
                "-genkeypair",
                "-alias",
                "test",
                "-keyalg",
                "RSA",
                "-storetype",
                "PKCS12",
                "-keystore",
                store.toString(),
                "-storepass",
                "changeit",
                "-keypass",
                "changeit",
                "-dname",
                "CN=localhost",
                "-ext",
                "SAN=dns:localhost,ip:127.0.0.1",
                "-validity",
                "1")
            .redirectErrorStream(true)
            .start();
    ByteArrayOutputStream log = new ByteArrayOutputStream();
    byte[] buffer = new byte[1024];
    int r;
    while ((r = keytool.getInputStream().read(buffer)) != -1) log.write(buffer, 0, r);
    assertEquals(log.toString(), 0, keytool.waitFor());
    KeyStore ks = KeyStore.getInstance("PKCS12");
    try (InputStream in = Files.newInputStream(store)) {
      ks.load(in, "changeit".toCharArray());
    }
    KeyManagerFactory km = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
    km.init(ks, "changeit".toCharArray());
    TrustManagerFactory tm =
        TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
    tm.init(ks);
    SSLContext trusted = SSLContext.getInstance("TLS");
    trusted.init(km.getKeyManagers(), tm.getTrustManagers(), new SecureRandom());
    byte[] data = Files.readAllBytes(Paths.get("demo/quartier.ibx"));
    AtomicBoolean changed = new AtomicBoolean();
    HttpsServer server = HttpsServer.create(new InetSocketAddress("localhost", 0), 0);
    server.setHttpsConfigurator(new HttpsConfigurator(trusted));
    ExecutorService executor = Executors.newFixedThreadPool(4);
    server.setExecutor(executor);
    server.createContext(
        "/",
        exchange -> {
          try {
            String path = exchange.getRequestURI().getPath();
            if (path.equals("/redirect")) {
              exchange.getResponseHeaders().set("Location", "/data");
              exchange.sendResponseHeaders(302, -1);
              return;
            }
            if (path.equals("/downgrade")) {
              exchange.getResponseHeaders().set("Location", "http://localhost/data");
              exchange.sendResponseHeaders(302, -1);
              return;
            }
            if (path.equals("/slow"))
              try {
                Thread.sleep(400);
              } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
              }
            if (!path.equals("/noetag"))
              exchange.getResponseHeaders().set("ETag", changed.get() ? "\"new\"" : "\"original\"");
            if (path.equals("/full")) {
              exchange.sendResponseHeaders(200, data.length);
              exchange.getResponseBody().write(data);
              return;
            }
            String range = exchange.getRequestHeaders().getFirst("Range");
            String[] parts = range.substring(6).split("-");
            int start = Integer.parseInt(parts[0]), end = Integer.parseInt(parts[1]);
            exchange
                .getResponseHeaders()
                .set(
                    "Content-Range",
                    "bytes "
                        + (path.equals("/bad") ? start + 1 : start)
                        + "-"
                        + end
                        + "/"
                        + data.length);
            exchange.sendResponseHeaders(206, end - start + 1);
            exchange.getResponseBody().write(data, start, end - start + 1);
          } finally {
            exchange.close();
          }
        });
    server.start();
    String base = "https://localhost:" + server.getAddress().getPort();
    SSLSocketFactory previous = HttpsURLConnection.getDefaultSSLSocketFactory();
    try {
      try (IbxContainer ignored = IbxContainer.open(URI.create(base + "/data"))) {
        fail("Untrusted certificate accepted");
      } catch (SSLException expected) {
      }
      HttpsURLConnection.setDefaultSSLSocketFactory(trusted.getSocketFactory());
      try (IbxContainer c = IbxContainer.open(URI.create(base + "/redirect"))) {
        assertEquals(0, c.metrics().chunksRead);
        assertNotNull(new ch.interlis.ibx.navigation.Navigation(c).resolve("g0", null));
        changed.set(true);
        c.clearCache();
        try {
          c.getObject("g1").objects().count();
          fail();
        } catch (Exception expected) {
          assertTrue(expected.toString().contains("changed"));
        }
      } finally {
        changed.set(false);
      }
      for (String path : new String[] {"/bad", "/noetag", "/full", "/downgrade"})
        try (IbxContainer ignored = IbxContainer.open(URI.create(base + path))) {
          fail(path);
        } catch (IOException expected) {
        }
      RemoteOptions options = new RemoteOptions();
      options.allowFullDownload = true;
      try (IbxContainer c = IbxContainer.open(URI.create(base + "/full"), options)) {
        assertNotNull(new ch.interlis.ibx.navigation.Navigation(c).resolve("g0", null));
      }
      options = new RemoteOptions();
      options.readTimeoutMillis = 100;
      try (IbxContainer ignored = IbxContainer.open(URI.create(base + "/slow"), options)) {
        fail("Timeout missing");
      } catch (SocketTimeoutException expected) {
      }
    } finally {
      HttpsURLConnection.setDefaultSSLSocketFactory(previous);
      server.stop(0);
      executor.shutdownNow();
    }
  }
}
