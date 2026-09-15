package ch.interlis.ilicontainer.codec;

import ch.interlis.ilicontainer.api.TransferMetadata;
import ch.interlis.iom.IomObject;
import ch.interlis.iom_j.Iom_jObject;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.*;
import java.io.*;
import java.math.*;
import java.util.*;

/** Explicit recursive IOM representation, never Java serialization. */
public final class ObjectCodec {
  private final TransferMetadata metadata;
  private final Map<String, Integer> ids = new HashMap<String, Integer>();
  private boolean frozen;

  public ObjectCodec(TransferMetadata metadata, boolean frozen) {
    this.metadata = metadata;
    this.frozen = frozen;
    for (int i = 0; i < metadata.dictionary.size(); i++) ids.put(metadata.dictionary.get(i), i);
  }

  private int id(String name) {
    Integer n = ids.get(name);
    if (n == null) {
      if (frozen) throw new IllegalArgumentException("Unknown dictionary name: " + name);
      n = ids.size();
      ids.put(name, n);
      metadata.dictionary.add(name);
    }
    return n;
  }

  private String name(int id) throws IOException {
    if (id < 0 || id >= metadata.dictionary.size())
      throw new IOException("Invalid dictionary id " + id);
    return metadata.dictionary.get(id);
  }

  public byte[] encode(IomObject o) throws IOException {
    return Cbor.bytes(node(o));
  }

  private ArrayNode node(IomObject o) {
    ArrayNode a = Cbor.MAPPER.createArrayNode();
    a.add(id(o.getobjecttag()));
    a.add(o.getobjectoid());
    a.add(o.getobjectrefoid());
    a.add(o.getobjectrefbid());
    a.add(o.getobjectreforderpos());
    a.add(o.getobjectoperation());
    a.add(o.getobjectconsistency());
    ArrayNode attrs = a.addArray();
    for (int i = 0; i < o.getattrcount(); i++) {
      String key = o.getattrname(i);
      ArrayNode field = attrs.addArray();
      field.add(id(key));
      ArrayNode values = field.addArray();
      for (int j = 0; j < o.getattrvaluecount(key); j++) {
        IomObject child = o.getattrobj(key, j);
        if (child != null) values.add(node(child));
        else {
          String value = o.getattrprim(key, j);
          boolean number =
              metadata.numericTypes.containsKey(o.getobjecttag() + "." + key)
                  || ((o.getobjecttag().equals("COORD") || o.getobjecttag().equals("ARC"))
                      && key.matches("[CAR][123]?"));
          if (value != null && number && metadata.numericEncoding.equals("decimal")) {
            BigDecimal d = new BigDecimal(value);
            ObjectNode n = values.addObject();
            n.put("m", d.unscaledValue().toByteArray());
            n.put("s", d.scale());
          } else values.add(value);
        }
      }
    }
    return a;
  }

  public IomObject decode(byte[] bytes) throws IOException {
    return object(Cbor.MAPPER.readTree(bytes));
  }

  public IomObject object(JsonNode a) throws IOException {
    if (!a.isArray() || a.size() != 8) throw new IOException("Invalid object record");
    Iom_jObject o = new Iom_jObject(name(a.get(0).intValue()), str(a.get(1)));
    o.setobjectrefoid(str(a.get(2)));
    o.setobjectrefbid(str(a.get(3)));
    o.setobjectreforderpos(a.get(4).longValue());
    o.setobjectoperation(a.get(5).intValue());
    o.setobjectconsistency(a.get(6).intValue());
    for (JsonNode field : a.get(7)) {
      String key = name(field.get(0).intValue());
      JsonNode values = field.get(1);
      if (values.size() == 0) o.setattrundefined(key);
      for (JsonNode v : values) {
        if (v.isArray()) o.addattrobj(key, object(v));
        else if (v.isObject())
          o.addattrvalue(
              key,
              new BigDecimal(new BigInteger(v.get("m").binaryValue()), v.get("s").intValue())
                  .toPlainString());
        else o.addattrvalue(key, str(v));
      }
    }
    return o;
  }

  private static String str(JsonNode n) {
    return n == null || n.isNull() ? null : n.asText();
  }
}
