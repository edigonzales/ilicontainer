package ch.interlis.ilicontainer.api;

public final class ReadMetrics {
  public long requests,
      bytesRead,
      indexBytes,
      chunkBytes,
      metadataBytes,
      cacheHits,
      chunksRead,
      indexPages;

  public void reset() {
    requests =
        bytesRead =
            indexBytes = chunkBytes = metadataBytes = cacheHits = chunksRead = indexPages = 0;
  }
}
