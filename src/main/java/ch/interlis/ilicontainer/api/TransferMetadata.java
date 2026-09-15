package ch.interlis.ilicontainer.api;

import ch.interlis.iom_j.xtf.XtfStartTransferEvent;
import java.util.*;

public final class TransferMetadata {
  public int mappingVersion = 1;
  public String sender, comment, version = "2.4", numericEncoding = "lexical";
  public List<String> dictionary = new ArrayList<String>();
  public List<String> transferModels = new ArrayList<String>();
  public Map<String, String> xmlNames = new TreeMap<String, String>();
  public Map<String, List<Property>> classes = new TreeMap<String, List<Property>>();
  public Set<String> topics = new TreeSet<String>();
  public List<ModelInfo> models = new ArrayList<ModelInfo>();
  public List<SourceInfo> sources = new ArrayList<SourceInfo>();
  public Map<String, String> numericTypes = new TreeMap<String, String>();
  public Map<String, String> geometryCrs = new TreeMap<String, String>();

  public XtfStartTransferEvent event() {
    return new XtfStartTransferEvent(sender, comment, version);
  }

  public static final class Property {
    public String name, enumType, baseDefInClass;
    public boolean oid, blackboxXml, blackboxBin, finalType, multiSurfaceOrArea;
  }

  public static final class ModelInfo {
    public String name, version, issuer, sourceDigest;
  }

  public static final class SourceInfo {
    public String name, origin, sha256;
    public byte[] content;
  }
}
