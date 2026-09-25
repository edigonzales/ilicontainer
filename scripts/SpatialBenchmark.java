import ch.interlis.ibx.api.*;
import ch.interlis.ibx.benchmark.RangeServer;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

public class SpatialBenchmark {
  static ObjectMapper json = new ObjectMapper();

  static String query(
      IbxContainer c, String cls, String attr, String tid, double x, double y, double radius)
      throws Exception {
    MessageDigest hash = MessageDigest.getInstance("SHA-256");
    long count = 0;
    if (radius >= 0) {
      try (Fragment f =
              c.querySpatialCandidates(
                  cls, attr, new BoundingBox(x - radius, y - radius, x + radius, y + radius));
          ch.interlis.ibx.container.CloseableIterator<ch.interlis.ibx.container.Location> it =
              f.locations()) {
        while (it.hasNext()) {
          ch.interlis.ibx.container.Location loc = it.next();
          hash.update(
              (loc.basketPosition + ":" + loc.chunkId + ":" + loc.ordinal + "\n")
                  .getBytes("UTF-8"));
          count++;
        }
      }
    } else {
      try (Fragment f = c.getObject(tid);
          java.util.stream.Stream<SelectedObject> stream = f.objects()) {
        Iterator<SelectedObject> it = stream.iterator();
        while (it.hasNext()) {
          hash.update((it.next().getObject().getobjectoid() + "\n").getBytes("UTF-8"));
          count++;
        }
      }
    }
    return count + ":" + java.util.HexFormat.of().formatHex(hash.digest());
  }

  public static void main(String[] a) throws Exception {
    Path file = Path.of(a[0]);
    String cls = a[1], attr = a[2], tid = a[3];
    double x = Double.parseDouble(a[4]), y = Double.parseDouble(a[5]);
    RemoteOptions options = new RemoteOptions();
    options.prefetchPositions = 0; // Measure index selection without fetching object chunks.
    for (String transport : new String[] {"local", "http"})
      try (RangeServer server = new RangeServer(file)) {
        for (double radius :
            attr.equals("-") ? new double[] {-1} : new double[] {-1, 20, 1000, 10000})
          for (String cache : new String[] {"cold", "warm"}) {
            try (IbxContainer c =
                transport.equals("local")
                    ? IbxContainer.open(file, options)
                    : IbxContainer.open(server.uri(), options)) {
              for (int warmup = 0; warmup < 3; warmup++) query(c, cls, attr, tid, x, y, radius);
              List<Object> runs = new ArrayList<>();
              String expected = null;
              for (int i = 0; i < 10; i++) {
                if (cache.equals("cold")) c.clearCache();
                c.metrics().reset();
                long start = System.nanoTime();
                String result = query(c, cls, attr, tid, x, y, radius);
                double ms = (System.nanoTime() - start) / 1e6;
                if (expected != null && !expected.equals(result))
                  throw new Exception("Unstable results");
                expected = result;
                Map<String, Object> run = new LinkedHashMap<>();
                run.put("ms", ms);
                run.put("metrics", json.convertValue(c.metrics(), Map.class));
                runs.add(run);
              }
              System.out.println(
                  json.writeValueAsString(
                      Map.of(
                          "reader",
                          "java",
                          "file",
                          file.getFileName().toString(),
                          "transport",
                          transport,
                          "cache",
                          cache,
                          "radius",
                          radius,
                          "result",
                          expected,
                          "runs",
                          runs)));
            }
          }
      }
  }
}
