package ch.interlis.ilicontainer.container;

import ch.interlis.ilicontainer.codec.*;
import ch.interlis.iom.IomObject;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.*;
import java.io.*;
import java.util.*;

public final class ObjectCursor implements CloseableIterator<IomObject> {
  private final JsonParser parser;
  private final ObjectCodec codec;
  private int remaining;

  public ObjectCursor(Chunk chunk, ObjectCodec codec) throws IOException {
    parser = Cbor.MAPPER.getFactory().createParser(chunk.objects);
    this.codec = codec;
    remaining = chunk.info.count;
  }

  public boolean hasNext() {
    return remaining > 0;
  }

  public IomObject next() {
    if (!hasNext()) throw new NoSuchElementException();
    try {
      JsonNode node = Cbor.MAPPER.readTree(parser);
      if (node == null) throw new EOFException("Too few objects in chunk");
      IomObject o = codec.object(node);
      remaining--;
      if (remaining == 0 && parser.nextToken() != null)
        throw new IOException("Too many objects in chunk");
      return o;
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
  }

  public void close() throws IOException {
    parser.close();
    remaining = 0;
  }
}
