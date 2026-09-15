package ch.interlis.ilicontainer.container;

import ch.interlis.ilicontainer.api.ReadMetrics;
import ch.interlis.ilicontainer.remote.RangeSource;
import java.io.*;
import java.util.*;

public final class FrameStore {
  public final RangeSource source;
  public final ReadMetrics metrics;
  private final long budget;
  private long used;
  private final LinkedHashMap<Long, Frames.Frame> cache =
      new LinkedHashMap<Long, Frames.Frame>(16, .75f, true);

  public FrameStore(RangeSource source, ReadMetrics metrics, long budget) {
    this.source = source;
    this.metrics = metrics;
    this.budget = budget;
  }

  public synchronized Frames.Frame read(long offset) throws IOException {
    Frames.Frame f = cache.get(offset);
    if (f != null) {
      metrics.cacheHits++;
      return f;
    }
    f = Frames.read(source, offset);
    long size = f.data.length + Frames.FRAME_HEADER;
    if (f.type == Frames.CHUNK) {
      metrics.chunkBytes += size;
      metrics.chunksRead++;
    } else if (f.type >= Frames.LEAF) {
      metrics.indexBytes += size;
      metrics.indexPages++;
    } else metrics.metadataBytes += size;
    if (size <= budget) {
      while (used + size > budget && !cache.isEmpty()) {
        Map.Entry<Long, Frames.Frame> e = cache.entrySet().iterator().next();
        used -= e.getValue().data.length + Frames.FRAME_HEADER;
        cache.remove(e.getKey());
      }
      cache.put(offset, f);
      used += size;
    }
    return f;
  }

  public void clear() {
    cache.clear();
    used = 0;
  }
}
