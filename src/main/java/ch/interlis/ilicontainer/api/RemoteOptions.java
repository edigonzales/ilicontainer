package ch.interlis.ilicontainer.api;

public final class RemoteOptions {
  public boolean immutableUrl;
  public boolean allowFullDownload;
  public int connectTimeoutMillis = 15000;
  public int readTimeoutMillis = 60000;
  public long cacheBytes = 32L * 1024 * 1024;
}
