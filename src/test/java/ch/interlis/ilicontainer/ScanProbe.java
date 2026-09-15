package ch.interlis.ilicontainer;

import ch.interlis.ilicontainer.api.IliContainer;
import ch.interlis.iox.*;
import java.nio.file.*;

public final class ScanProbe {
  public static void main(String[] args) throws Exception {
    if (args.length == 3) {
      ch.interlis.ilicontainer.api.WriterOptions w =
          new ch.interlis.ilicontainer.api.WriterOptions();
      w.modelFiles.add(args[2]);
      w.sortMemoryBytes = 1024 * 1024;
      ch.interlis.ilicontainer.container.ContainerWriter.create(
          Paths.get(args[0]), Paths.get(args[1]), w);
      return;
    }
    IoxReader reader = IliContainer.stream(Files.newInputStream(Paths.get(args[0])));
    long n = 0;
    try {
      IoxEvent e;
      while ((e = reader.read()) != null) if (e instanceof ObjectEvent) n++;
    } finally {
      reader.close();
    }
    System.out.println(n);
  }
}
