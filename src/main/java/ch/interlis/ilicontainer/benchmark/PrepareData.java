package ch.interlis.ilicontainer.benchmark;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.security.*;
import java.time.Instant;
import java.util.*;
import java.util.zip.*;

/** Explicit benchmark preparation; never invoked by the normal test task. */
public final class PrepareData {
  private static final String LOCALITIES =
      "https://data.geo.admin.ch/ch.swisstopo-vd.ortschaftenverzeichnis_plz/ortschaftenverzeichnis_plz/ortschaftenverzeichnis_plz_2056.xtf.zip";
  private static final String ADDRESSES =
      "https://data.geo.admin.ch/ch.swisstopo.amtliches-gebaeudeadressverzeichnis/amtliches-gebaeudeadressverzeichnis_ch/amtliches-gebaeudeadressverzeichnis_ch_2056.xtf.zip";

  public static void main(String[] args) throws Exception {
    if (args.length < 2 || args.length > 3)
      throw new IllegalArgumentException(
          "Usage: PrepareData dmav|dmav-fixpoints|dmav-pipes|localities|addresses"
              + " OUTPUT_DIRECTORY");
    Path dir = Paths.get(args[1]).toAbsolutePath();
    Files.createDirectories(dir);
    String community = args.length == 3 ? args[2] : "2541";
    if (!community.matches("[0-9]{4}"))
      throw new IllegalArgumentException("Expected four-digit community number");
    String url;
    if (args[0].equals("dmav")) url = dmavUrl("toleranzstufen", community);
    else if (args[0].equals("dmav-fixpoints")) url = dmavUrl("fixpunkteavkategorie3", community);
    else if (args[0].equals("dmav-pipes")) url = dmavUrl("rohrleitungen", community);
    else if (args[0].equals("localities")) url = LOCALITIES;
    else if (args[0].equals("addresses")) url = ADDRESSES;
    else throw new IllegalArgumentException("Unknown dataset");
    Path download = dir.resolve(url.endsWith("zip") ? "source.zip" : "source.xtf");
    Map<String, Object> manifest = new LinkedHashMap<String, Object>();
    manifest.put("url", url);
    manifest.put("retrievedAt", Instant.now().toString());
    if (!Files.exists(download)) download(url, download);
    manifest.put("retrievedAt", Files.getLastModifiedTime(download).toInstant().toString());
    manifest.put("downloadBytes", Files.size(download));
    manifest.put("sha256", digest(download));
    List<Map<String, Object>> members = new ArrayList<Map<String, Object>>();
    if (url.endsWith("zip")) {
      try (ZipInputStream zip = new ZipInputStream(Files.newInputStream(download))) {
        ZipEntry e;
        while ((e = zip.getNextEntry()) != null) {
          if (e.isDirectory() || (!e.getName().endsWith(".xtf") && !e.getName().endsWith(".ili")))
            continue;
          Path p = dir.resolve(e.getName()).normalize();
          if (!p.startsWith(dir)) throw new IOException("Unsafe archive path");
          Files.createDirectories(p.getParent());
          try (OutputStream out = Files.newOutputStream(p)) {
            copy(zip, out);
          }
          members.add(member(dir, p, e.getName()));
        }
      }
    } else members.add(member(dir, download, null));
    manifest.put("members", members);
    new ObjectMapper()
        .writerWithDefaultPrettyPrinter()
        .writeValue(dir.resolve("manifest.json").toFile(), manifest);
    System.out.println(dir.resolve("manifest.json"));
  }

  private static String dmavUrl(String component, String community) throws Exception {
    String catalog = "https://data.geo.so.ch/ilidata.xml";
    javax.xml.parsers.DocumentBuilderFactory f =
        javax.xml.parsers.DocumentBuilderFactory.newInstance();
    f.setNamespaceAware(true);
    f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
    org.w3c.dom.Document d;
    try (InputStream in = new URL(catalog).openStream()) {
      d = f.newDocumentBuilder().parse(in);
    }
    org.w3c.dom.NodeList paths = d.getElementsByTagNameNS("*", "path");
    for (int i = 0; i < paths.getLength(); i++) {
      String p = paths.item(i).getTextContent();
      if (p.endsWith(community + ".ch.so.agi.dmav.relational." + component + ".xtf"))
        return new URI(catalog).resolve(p).toString();
    }
    throw new IOException("Requested DMAV dataset no longer listed");
  }

  private static Map<String, Object> member(Path dir, Path file, String zipMember)
      throws Exception {
    Map<String, Object> m = new LinkedHashMap<String, Object>();
    m.put("file", dir.relativize(file).toString());
    m.put("zipMember", zipMember);
    m.put("bytes", Files.size(file));
    m.put("sha256", digest(file));
    if (file.toString().endsWith(".xtf")) {
      javax.xml.stream.XMLInputFactory f = javax.xml.stream.XMLInputFactory.newFactory();
      f.setProperty(javax.xml.stream.XMLInputFactory.SUPPORT_DTD, false);
      f.setProperty("javax.xml.stream.isSupportingExternalEntities", false);
      List<String> models = new ArrayList<String>();
      boolean full = true;
      String ns = null;
      try (InputStream in = Files.newInputStream(file)) {
        javax.xml.stream.XMLStreamReader r = f.createXMLStreamReader(in);
        while (r.hasNext()) {
          int event = r.next();
          if (event == javax.xml.stream.XMLStreamConstants.START_ELEMENT) {
            if (ns == null) ns = r.getNamespaceURI();
            if ("model".equals(r.getLocalName())
                && "http://www.interlis.ch/xtf/2.4/INTERLIS".equals(r.getNamespaceURI())) {
              models.add(r.getElementText());
              continue;
            }
            if ("MODEL".equals(r.getLocalName())
                && "http://www.interlis.ch/INTERLIS2.3".equals(r.getNamespaceURI())) {
              String name = r.getAttributeValue(null, "NAME");
              if (name != null) models.add(name);
            }
            for (int a = 0; a < r.getAttributeCount(); a++) {
              String name = r.getAttributeLocalName(a), v = r.getAttributeValue(a);
              if ((name.equalsIgnoreCase("kind") && !v.equalsIgnoreCase("FULL"))
                  || name.equalsIgnoreCase("startstate")
                  || name.equalsIgnoreCase("endstate")) full = false;
            }
          }
        }
        r.close();
      }
      m.put("namespace", ns);
      m.put("models", models);
      m.put("full", full);
      m.put("supportedTransfer", "http://www.interlis.ch/xtf/2.4/INTERLIS".equals(ns) && full);
    }
    return m;
  }

  private static void download(String url, Path target) throws IOException {
    URLConnection c = new URL(url).openConnection();
    c.setConnectTimeout(15000);
    c.setReadTimeout(60000);
    Path temp = Files.createTempFile(target.getParent(), "download-", ".tmp");
    try {
      try (InputStream in = c.getInputStream();
          OutputStream out = Files.newOutputStream(temp)) {
        copy(in, out);
      }
      long size = c.getContentLengthLong();
      if (size >= 0 && size != Files.size(temp)) throw new IOException("Truncated download");
      Files.move(temp, target, StandardCopyOption.REPLACE_EXISTING);
    } finally {
      Files.deleteIfExists(temp);
    }
  }

  private static void copy(InputStream in, OutputStream out) throws IOException {
    byte[] b = new byte[65536];
    int n;
    while ((n = in.read(b)) != -1) out.write(b, 0, n);
  }

  public static String digest(Path file) throws Exception {
    MessageDigest d = MessageDigest.getInstance("SHA-256");
    try (InputStream in = Files.newInputStream(file)) {
      byte[] b = new byte[65536];
      int n;
      while ((n = in.read(b)) != -1) d.update(b, 0, n);
    }
    StringBuilder s = new StringBuilder();
    for (byte x : d.digest()) s.append(String.format("%02x", x & 255));
    return s.toString();
  }
}
