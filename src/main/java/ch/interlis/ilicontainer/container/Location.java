package ch.interlis.ilicontainer.container;

public final class Location {
  public long chunkOffset, basketOffset, basketPosition, chunkId;
  public int ordinal = -1;

  public Location() {}

  public Location(long chunk, long basket, long position, long id, int ordinal) {
    chunkOffset = chunk;
    basketOffset = basket;
    basketPosition = position;
    chunkId = id;
    this.ordinal = ordinal;
  }
}
