package ch.interlis.ibx.container;

import ch.interlis.ibx.api.*;
import ch.interlis.ibx.codec.*;
import ch.interlis.ibx.index.*;
import ch.interlis.ibx.iox.*;
import ch.interlis.iom.*;
import ch.interlis.iom_j.xtf.*;
import ch.interlis.iox.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public final class ContainerWriter {
  public static void create(Path input, Path target, WriterOptions options) throws Exception {
    options.validate();
    target = target.toAbsolutePath();
    if (Files.exists(target) && !options.overwrite)
      throw new FileAlreadyExistsException(target.toString());
    Path parent = target.getParent();
    Files.createDirectories(parent);
    Path temp =
        options.temporaryDirectory == null
            ? Files.createTempDirectory(parent, ".ibx-work-")
            : Files.createTempDirectory(options.temporaryDirectory, "ibx-work-");
    Path output = Files.createTempFile(parent, ".ibx-output-", ".tmp");
    TemporaryUsage usage = new TemporaryUsage(temp, output);
    options.objectDirectoryEntryBytes = 0;
    try {
      ModelBridge bridge = ModelBridge.load(input, options, temp);
      for (Map.Entry<String, String> order : options.spatialOrder.entrySet()) {
        if (!bridge.metadata.geometryCrs.containsKey(order.getKey() + "." + order.getValue()))
          throw new IOException(
              "Unknown direct geometry attribute for spatial ordering: "
                  + order.getKey()
                  + "."
                  + order.getValue());
      }
      bridge.metadata.spatialOrder.putAll(options.spatialOrder);
      bridge.metadata.reverseIndex = options.reverseIndex;
      ObjectCodec codec = new ObjectCodec(bridge.metadata, false);
      try (ExternalSort objects = new ExternalSort(temp, options.sortMemoryBytes);
          ExternalSort index = new ExternalSort(temp, options.sortMemoryBytes, true);
          ch.interlis.ibx.navigation.NavigationBuilder navigation =
              new ch.interlis.ibx.navigation.NavigationBuilder(temp, options, bridge.metadata)) {
        spool(input, bridge, codec, objects, temp);
        options.geometryVerificationNanos = bridge.metadata.geometryVerificationNanos;
        try (RandomAccessFile out = new RandomAccessFile(output.toFile(), "rw");
            CloseableIterator<ExternalSort.Entry> records =
                ch.interlis.ibx.spatial.SpatialOrder.reorder(
                    objects.finish(), codec, bridge.metadata, options, temp)) {
          Frames.header(out);
          com.fasterxml.jackson.databind.node.ObjectNode storedMetadata =
              Cbor.MAPPER.valueToTree(bridge.metadata);
          Frames.write(out, Frames.METADATA, Cbor.bytes(storedMetadata));
          BasketContext basket = null;
          long basketOffset = 0, basketLength = 0, chunkId = 0, fid = 0;
          Chunk.Info info = null;
          ByteArrayOutputStream raw = new ByteArrayOutputStream();
          List<String> tids = new ArrayList<String>();
          while (records.hasNext()) {
            ExternalSort.Entry record = records.next();
            if (record.key.contains("\0!basket")) {
              if (info != null) {
                writeChunk(out, index, info, raw.toByteArray(), tids, options);
                info = null;
                raw.reset();
                tids.clear();
              }
              if (basket != null) Frames.write(out, Frames.END_BASKET, new byte[0]);
              basket = Cbor.read(record.value, BasketContext.class);
              basketOffset = Frames.write(out, Frames.BASKET, record.value);
              basketLength = out.getFilePointer() - basketOffset;
              Location loc =
                  new Location(0, basketOffset, basket.position, 0, -1).lengths(0, basketLength);
              byte[] locBytes = loc.bytes();
              index.add("B\0" + basket.bid, locBytes);
              index.add("P\0" + FilesEx.number(basket.position), locBytes);
              index.add(
                  "T\0" + basket.topic + "\0" + FilesEx.number(basket.position) + "\0!basket",
                  locBytes);
            } else {
              if (basket == null) throw new IOException("Object without basket");
              int first = record.key.indexOf('\0'), last = record.key.lastIndexOf('\0');
              String cls = record.key.substring(first + 1, last);
              if (info != null
                  && (!info.className.equals(cls)
                      || (raw.size() > 0
                          && (long) raw.size() + record.value.length > options.chunkSize))) {
                writeChunk(out, index, info, raw.toByteArray(), tids, options);
                info = null;
                raw.reset();
                tids.clear();
              }
              if (info == null) {
                info = new Chunk.Info();
                info.id = chunkId++;
                info.firstFid = fid;
                info.basketPosition = basket.position;
                info.basketOffset = basketOffset;
                info.basketLength = basketLength;
                info.className = cls;
                info.topic = basket.topic;
                info.bid = basket.bid;
                info.compression = options.compression;
              }
              navigation.accept(Cbor.MAPPER.readTree(record.value), fid, basket);
              raw.write(record.value);
              com.fasterxml.jackson.databind.JsonNode tid =
                  Cbor.MAPPER.readTree(record.value).get(1);
              tids.add(tid.isNull() ? null : tid.asText());
              info.count++;
              fid++;
            }
          }
          if (info != null) writeChunk(out, index, info, raw.toByteArray(), tids, options);
          if (basket != null) Frames.write(out, Frames.END_BASKET, new byte[0]);
          Frames.write(out, Frames.END_TRANSFER, new byte[0]);
          navigation.finish(index);
          long root;
          try (CloseableIterator<ExternalSort.Entry> sorted = index.finish()) {
            root = BTree.build(out, sorted, temp);
          }
          Frames.footer(out, root, 0);
          out.getFD().sync();
        }
      }
      FilesEx.publish(output, target, options.overwrite);
    } finally {
      usage.close();
      options.temporaryPeakSampledBytes = usage.peak();
      Files.deleteIfExists(output);
      FilesEx.deleteTree(temp);
    }
  }

  private static void spool(
      Path input, ModelBridge bridge, ObjectCodec codec, ExternalSort objects, Path temp)
      throws Exception {
    Xtf24Reader reader = new Xtf24Reader(input.toFile());
    reader.setModel(bridge.model);
    long basket = -1, ordinal = 0;
    boolean inside = false, ended = false;
    String bid = null;
    BasketContext currentBasket = null;
    try {
      IoxEvent e;
      while ((e = reader.read()) != null) {
        if (e instanceof StartBasketEvent) {
          if (inside) throw new IOException("Nested baskets");
          StartBasketEvent start = (StartBasketEvent) e;
          if (start.getKind() != IomConstants.IOM_FULL
              || start.getStartstate() != null
              || start.getEndstate() != null)
            throw new IOException("Only FULL transfers are supported; INITIAL/UPDATE rejected");
          if (start.getBid() == null || start.getBid().isEmpty())
            throw new IOException("Missing BID");
          BasketContext context = new BasketContext(start, ++basket);
          bid = context.bid;
          currentBasket = context;
          objects.add(FilesEx.number(basket) + "\0!basket", Cbor.bytes(context));
          inside = true;
        } else if (e instanceof ObjectEvent) {
          if (!inside) throw new IOException("Object outside basket");
          IomObject obj = ((ObjectEvent) e).getIomObject();
          if (obj.getobjectoperation() != IomConstants.IOM_OP_INSERT)
            throw new IOException("Non-FULL object operation");
          // OID-less association instances remain in class/basket scans; no invented INTERLIS
          // identity.
          if (obj.getobjectoid() == null) {
            ch.interlis.ili2c.metamodel.Element def = bridge.model.getElement(obj.getobjecttag());
            if (!(def instanceof ch.interlis.ili2c.metamodel.AssociationDef))
              throw new IOException("Missing TID: " + obj.getobjecttag());
          }
          try {
            if ("wkb".equals(bridge.metadata.geometryEncoding))
              bridge.resolveGeometryCrs(obj, currentBasket);
            objects.add(
                FilesEx.number(basket)
                    + "\0"
                    + obj.getobjecttag()
                    + "\0"
                    + FilesEx.number(ordinal++),
                codec.encode(obj));
          } catch (IOException ex) {
            throw new IOException(
                "BID=" + bid + " TID=" + obj.getobjectoid() + ": " + ex.getMessage(), ex);
          }
        } else if (e instanceof EndBasketEvent) {
          if (!inside) throw new IOException("Unexpected basket end");
          inside = false;
        } else if (e instanceof EndTransferEvent) {
          if (inside) throw new IOException("Unclosed basket");
          ended = true;
          break;
        }
      }
      if (!ended) throw new IOException("Incomplete transfer");
    } finally {
      reader.close();
    }
  }

  private static void writeChunk(
      RandomAccessFile out,
      ExternalSort index,
      Chunk.Info info,
      byte[] raw,
      List<String> tids,
      WriterOptions options)
      throws IOException {
    byte[] packed = Chunk.pack(info, raw, options.compressionLevel);
    long offset = Frames.write(out, Frames.CHUNK, packed);
    Location all =
        new Location(offset, info.basketOffset, info.basketPosition, info.id, -1)
            .lengths(packed.length + Frames.FRAME_HEADER, info.basketLength);
    byte[] data = all.bytes();
    String order = FilesEx.number(info.basketPosition) + "\0" + FilesEx.number(info.id);
    index.add("C\0" + info.className + "\0" + order, data);
    index.add("D\0" + order, data);
    index.add("T\0" + info.topic + "\0" + order, data);
    index.add(
        "F\0" + FilesEx.number(info.firstFid),
        java.nio.ByteBuffer.allocate(57).put(all.bytes()).putInt(info.count).array());
    for (int i = 0; i < tids.size(); i++) {
      if (tids.get(i) != null) {
        String key = "O\0" + tids.get(i);
        byte[] value =
            new Location(offset, info.basketOffset, info.basketPosition, info.id, i)
                .lengths(packed.length + Frames.FRAME_HEADER, info.basketLength)
                .bytes();
        index.add(key, value);
        options.objectDirectoryEntryBytes += 8 + key.getBytes("UTF-8").length + value.length;
      }
    }
  }
}
