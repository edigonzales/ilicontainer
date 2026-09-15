package ch.interlis.ilicontainer.iox;

import ch.interlis.ili2c.config.Configuration;
import ch.interlis.ili2c.metamodel.*;
import ch.interlis.ilicontainer.api.*;
import ch.interlis.ilicontainer.container.FilesEx;
import ch.interlis.ilirepository.IliManager;
import ch.interlis.iom.*;
import ch.interlis.iom_j.*;
import ch.interlis.iom_j.xtf.*;
import ch.interlis.iom_j.xtf.impl.MyHandler;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public final class ModelBridge {
  public final TransferMetadata metadata;
  public final TransferDescription model;

  private ModelBridge(TransferMetadata m, TransferDescription td) {
    metadata = m;
    model = td;
  }

  public static ModelBridge load(Path input, WriterOptions options, Path temp) throws Exception {
    Xtf24Reader reader = new Xtf24Reader(input.toFile());
    XtfStartTransferEvent start;
    try {
      start = (XtfStartTransferEvent) reader.read();
    } catch (Exception e) {
      throw new IOException(
          "Only readable INTERLIS 2.4 FULL XTF is supported: " + e.getMessage(), e);
    } finally {
      reader.close();
    }
    TransferMetadata meta = new TransferMetadata();
    meta.sender = start.getSender();
    meta.comment = start.getComment();
    meta.numericEncoding = options.numericEncoding;
    if (meta.comment != null && meta.comment.contains("IliContainer fragment"))
      throw new IOException("A marked fragment cannot be imported as a FULL transfer");
    if (start.getHeaderObjects() != null) {
      List<Map.Entry<String, IomObject>> entries =
          new ArrayList<Map.Entry<String, IomObject>>(start.getHeaderObjects().entrySet());
      entries.sort(Comparator.comparing(e -> e.getKey()));
      for (Map.Entry<String, IomObject> e : entries) {
        String n = e.getValue().getattrvalue(MyHandler.HEADER_OBJECT_MODELENTRY_NAME);
        if (n != null) meta.transferModels.add(n);
      }
    }
    if (meta.transferModels.isEmpty()) throw new IOException("No models declared in XTF header");
    IliManager manager = new IliManager();
    manager.setCache(temp.resolve("models").toFile());
    List<String> paths = new ArrayList<String>();
    paths.add(input.toAbsolutePath().getParent().toString());
    paths.addAll(options.modelPaths);
    manager.setRepositories(paths.toArray(new String[0]));
    Configuration config;
    if (!options.modelFiles.isEmpty())
      config = manager.getConfigWithFiles(new ArrayList<String>(options.modelFiles));
    else config = manager.getConfig(new ArrayList<String>(meta.transferModels), 2.4);
    TransferDescription td = ch.interlis.ili2c.Main.runCompiler(config);
    if (td == null)
      throw new IOException(
          "INTERLIS models could not be compiled; supply --model-file or --model-dir");
    ViewableProperties mapping = Ili2cUtility.getIoxMappingTable(td);
    if (mapping.getXtf24nameMapping() == null)
      throw new IOException("Expected INTERLIS 2.4 model mapping");
    meta.xmlNames.putAll(mapping.getXtf24nameMapping());
    collect(td, mapping, meta);
    Map<String, String> digests = new HashMap<String, String>();
    for (Iterator<?> it = td.iterator(); it.hasNext(); ) {
      Object next = it.next();
      if (!(next instanceof Model) || next instanceof PredefinedModel) continue;
      Model m = (Model) next;
      TransferMetadata.ModelInfo mi = new TransferMetadata.ModelInfo();
      mi.name = m.getName();
      mi.version = m.getModelVersion();
      mi.issuer = m.getIssuer();
      if (m.getFileName() != null) {
        Path file = Paths.get(m.getFileName());
        String canonical = file.toAbsolutePath().normalize().toString();
        String digest = digests.get(canonical);
        if (digest == null) {
          byte[] data = Files.readAllBytes(file);
          digest = FilesEx.sha256(data);
          digests.put(canonical, digest);
          TransferMetadata.SourceInfo si = new TransferMetadata.SourceInfo();
          si.name = file.getFileName().toString();
          si.origin = sourceOrigin(file, temp, paths);
          si.sha256 = digest;
          if (options.embedModels) si.content = data;
          meta.sources.add(si);
        }
        mi.sourceDigest = digest;
      }
      meta.models.add(mi);
    }
    for (String n : meta.transferModels)
      if (td.getElement(Model.class, n) == null)
        throw new IOException("Header model not resolved: " + n);
    return new ModelBridge(meta, td);
  }

  private static String sourceOrigin(Path file, Path temp, List<String> repositories) {
    Path cache = temp.resolve("models").toAbsolutePath().normalize();
    Path resolved = file.toAbsolutePath().normalize();
    if (resolved.startsWith(cache)) {
      String relative = cache.relativize(resolved).toString().replace(File.separatorChar, '/');
      for (String repo : repositories) {
        if (repo.startsWith("https://") || repo.startsWith("http://")) {
          java.net.URI uri = java.net.URI.create(repo);
          if (relative.startsWith(uri.getAuthority() + "/"))
            return uri.getScheme() + "://" + relative;
        }
      }
      return "repository-cache:" + relative;
    }
    return resolved.toUri().toString();
  }

  private static void collect(
      ch.interlis.ili2c.metamodel.Container<?> container,
      ViewableProperties mapping,
      TransferMetadata meta) {
    for (Iterator<?> it = container.iterator(); it.hasNext(); ) {
      Object next = it.next();
      if (!(next instanceof Element)) continue;
      Element e = (Element) next;
      String tag = e.getScopedName(null);
      if (e instanceof Topic) meta.topics.add(tag);
      if (e instanceof Viewable && mapping.existsClass(tag)) {
        List<TransferMetadata.Property> props = new ArrayList<TransferMetadata.Property>();
        for (ViewableProperty p : mapping.getClassVProperties(tag)) {
          TransferMetadata.Property v = new TransferMetadata.Property();
          v.name = p.getName();
          v.enumType = p.getEnumType();
          v.baseDefInClass = p.getBaseDefInClass();
          v.oid = p.isTypeOid();
          v.blackboxXml = p.isTypeBlackboxXml();
          v.blackboxBin = p.isTypeBlackboxBin();
          v.finalType = p.isTypeFinal();
          v.multiSurfaceOrArea = p.isMultiSurfaceOrAreaType();
          props.add(v);
        }
        meta.classes.put(tag, props);
        Iterator<?> attrs = ((Viewable) e).getAttributesAndRoles2();
        while (attrs.hasNext()) {
          ViewableTransferElement ve = (ViewableTransferElement) attrs.next();
          if (ve.obj instanceof AttributeDef) {
            AttributeDef a = (AttributeDef) ve.obj;
            Type type = a.getDomainResolvingAll();
            String key = tag + "." + a.getName();
            if (type instanceof NumericType)
              meta.numericTypes.put(
                  key,
                  String.valueOf(
                      ((NumericType) type).getMinimum() == null
                          ? 0
                          : ((NumericType) type).getMinimum().getAccuracy()));
            AbstractCoordType coord = null;
            if (type instanceof AbstractCoordType) coord = (AbstractCoordType) type;
            else if (type instanceof LineType) {
              Domain d = ((LineType) type).getControlPointDomain();
              if (d != null && d.getType().resolveAliases() instanceof AbstractCoordType)
                coord = (AbstractCoordType) d.getType().resolveAliases();
            }
            if (coord != null) {
              String crs = coord.getCrs(a);
              meta.geometryCrs.put(key, crs == null ? "" : crs);
            }
          }
        }
      }
      if (e instanceof ch.interlis.ili2c.metamodel.Container && !(e instanceof PredefinedModel))
        collect((ch.interlis.ili2c.metamodel.Container<?>) e, mapping, meta);
    }
  }

  public static ViewableProperties mapping(TransferMetadata meta) throws IOException {
    if (meta.mappingVersion != 1) throw new IOException("Unknown model mapping version");
    ViewableProperties out = new ViewableProperties();
    out.setXtf24nameMapping(new HashMap<String, String>(meta.xmlNames));
    for (Map.Entry<String, List<TransferMetadata.Property>> entry : meta.classes.entrySet()) {
      List<ViewableProperty> props = new ArrayList<ViewableProperty>();
      for (TransferMetadata.Property v : entry.getValue()) {
        ViewableProperty p = new ViewableProperty(v.name);
        p.setEnumType(v.enumType);
        p.setBaseDefInClass(v.baseDefInClass);
        p.setTypeOid(v.oid);
        p.setTypeBlackboxXml(v.blackboxXml);
        p.setTypeBlackboxBin(v.blackboxBin);
        p.setTypeFinal(v.finalType);
        p.setTypeMultiSurfaceOrArea(v.multiSurfaceOrArea);
        props.add(p);
      }
      out.defineClass(entry.getKey(), props.toArray(new ViewableProperty[0]));
    }
    return out;
  }

  public static XtfWriterBase writer(OutputStream out, TransferMetadata meta) throws Exception {
    XtfWriterBase writer = new LosslessXtfWriter(out, meta);
    List<XtfModel> models = new ArrayList<XtfModel>();
    for (String name : meta.transferModels) models.add(new XtfModel(name, null, null));
    writer.setModels(models.toArray(new XtfModel[0]));
    return writer;
  }
}
