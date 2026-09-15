package ch.interlis.ilicontainer.spatial;

import ch.interlis.ilicontainer.api.BoundingBox;
import ch.interlis.iom.IomObject;
import ch.interlis.iom_j.itf.impl.jtsext.geom.ArcSegment;
import com.vividsolutions.jts.geom.*;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;

/** Geometry structure traversal; arcs are not linearized. */
public final class GeometryBounds {
  private GeometryBounds() {}

  public static BoundingBox attribute(IomObject object, String name) throws IOException {
    BoundingBox result = null;
    for (int i = 0; i < object.getattrvaluecount(name); i++) {
      IomObject g = object.getattrobj(name, i);
      if (g == null) {
        if (object.getattrprim(name, i) != null)
          throw new IOException("Non-geometry value in " + name);
        continue;
      }
      BoundingBox box = bounds(g);
      if (box != null) {
        if (result == null) result = box;
        else result.expand(box);
      }
    }
    return result;
  }

  public static BoundingBox bounds(IomObject geometry) throws IOException {
    Envelope envelope = new Envelope();
    walk(geometry, envelope);
    if (envelope.isNull()) return null;
    return new BoundingBox(
        envelope.getMinX(), envelope.getMinY(), envelope.getMaxX(), envelope.getMaxY());
  }

  private static Coordinate coord(IomObject o, String x, String y) throws IOException {
    try {
      String sx = o.getattrvalue(x), sy = o.getattrvalue(y);
      if (sx == null || sy == null) throw new IOException("Incomplete coordinate");
      double dx = new BigDecimal(sx).doubleValue(), dy = new BigDecimal(sy).doubleValue();
      if (!Double.isFinite(dx) || !Double.isFinite(dy))
        throw new IOException("Non-finite coordinate");
      return new Coordinate(dx, dy);
    } catch (NumberFormatException e) {
      throw new IOException("Invalid coordinate", e);
    }
  }

  private static void include(Envelope env, Coordinate c) {
    env.expandToInclude(Math.nextDown(c.x), Math.nextDown(c.y));
    env.expandToInclude(Math.nextUp(c.x), Math.nextUp(c.y));
  }

  private static BigDecimal number(IomObject o, String name) {
    return new BigDecimal(o.getattrvalue(name));
  }

  private static int angleCompare(BigDecimal x1, BigDecimal y1, BigDecimal x2, BigDecimal y2) {
    int h1 = y1.signum() > 0 || (y1.signum() == 0 && x1.signum() >= 0) ? 0 : 1;
    int h2 = y2.signum() > 0 || (y2.signum() == 0 && x2.signum() >= 0) ? 0 : 1;
    if (h1 != h2) return Integer.compare(h1, h2);
    return -x1.multiply(y2).subtract(y1.multiply(x2)).signum();
  }

  private static boolean between(
      BigDecimal sx, BigDecimal sy, BigDecimal ex, BigDecimal ey, BigDecimal dx, BigDecimal dy) {
    int ends = angleCompare(sx, sy, ex, ey);
    boolean after = angleCompare(sx, sy, dx, dy) <= 0;
    boolean before = angleCompare(dx, dy, ex, ey) <= 0;
    return ends <= 0 ? after && before : after || before;
  }

  private static void exactArcEnvelope(IomObject start, IomObject arc, Envelope env)
      throws IOException {
    BigDecimal x = number(start, "C1"), y = number(start, "C2");
    BigDecimal ax = number(arc, "A1").subtract(x), ay = number(arc, "A2").subtract(y);
    BigDecimal bx = number(arc, "C1").subtract(x), by = number(arc, "C2").subtract(y);
    BigDecimal determinant = ax.multiply(by).subtract(ay.multiply(bx));
    if (determinant.signum() == 0) throw new IOException("Collinear arc");
    BigDecimal den = determinant.multiply(BigDecimal.valueOf(2));
    BigDecimal aa = ax.multiply(ax).add(ay.multiply(ay)), bb = bx.multiply(bx).add(by.multiply(by));
    BigDecimal nx = aa.multiply(by).subtract(bb.multiply(ay));
    BigDecimal ny = ax.multiply(bb).subtract(bx.multiply(aa));
    if (den.signum() < 0) {
      den = den.negate();
      nx = nx.negate();
      ny = ny.negate();
    }
    BigDecimal sx = nx.negate(), sy = ny.negate();
    BigDecimal ex = bx.multiply(den).subtract(nx), ey = by.multiply(den).subtract(ny);
    BigDecimal radiusNumerator = nx.multiply(nx).add(ny.multiply(ny)),
        denSquared = den.multiply(den);
    double radius =
        Math.sqrt(radiusNumerator.divide(denSquared, MathContext.DECIMAL128).doubleValue());
    if (!Double.isFinite(radius) || radius <= 0)
      throw new IOException("Unrepresentable arc radius");
    while (new BigDecimal(radius).pow(2).multiply(denSquared).compareTo(radiusNumerator) < 0)
      radius = Math.nextUp(radius);
    BigDecimal r = new BigDecimal(radius);
    double lowerRadius = Math.nextDown(radius);
    while (new BigDecimal(lowerRadius).pow(2).multiply(denSquared).compareTo(radiusNumerator) > 0)
      lowerRadius = Math.nextDown(lowerRadius);
    BigDecimal lowerR = new BigDecimal(lowerRadius);
    BigDecimal cx = x.multiply(den).add(nx), cy = y.multiply(den).add(ny);
    if (determinant.signum() < 0) {
      BigDecimal t = sx;
      sx = ex;
      ex = t;
      t = sy;
      sy = ey;
      ey = t;
    }
    int[][] directions = {{1, 0}, {0, 1}, {-1, 0}, {0, -1}};
    for (int[] d : directions) {
      if (!between(sx, sy, ex, ey, BigDecimal.valueOf(d[0]), BigDecimal.valueOf(d[1]))) continue;
      BigDecimal lowX = cx.divide(den, 40, RoundingMode.FLOOR);
      BigDecimal highX = cx.divide(den, 40, RoundingMode.CEILING);
      BigDecimal lowY = cy.divide(den, 40, RoundingMode.FLOOR);
      BigDecimal highY = cy.divide(den, 40, RoundingMode.CEILING);
      if (d[0] < 0) {
        lowX = lowX.subtract(r);
        highX = highX.subtract(lowerR);
      }
      if (d[0] > 0) {
        lowX = lowX.add(lowerR);
        highX = highX.add(r);
      }
      if (d[1] < 0) {
        lowY = lowY.subtract(r);
        highY = highY.subtract(lowerR);
      }
      if (d[1] > 0) {
        lowY = lowY.add(lowerR);
        highY = highY.add(r);
      }
      env.expandToInclude(Math.nextDown(lowX.doubleValue()), Math.nextDown(lowY.doubleValue()));
      env.expandToInclude(Math.nextUp(highX.doubleValue()), Math.nextUp(highY.doubleValue()));
    }
  }

  private static void walk(IomObject o, Envelope env) throws IOException {
    String tag = o.getobjecttag();
    if (tag.equals("COORD")) {
      include(env, coord(o, "C1", "C2"));
      return;
    }
    if (tag.equals("SEGMENTS")) {
      Coordinate previous = null;
      IomObject previousObject = null;
      for (int i = 0; i < o.getattrvaluecount("segment"); i++) {
        IomObject segment = o.getattrobj("segment", i);
        if (segment == null) throw new IOException("Missing line segment");
        Coordinate end = coord(segment, "C1", "C2");
        if (segment.getobjecttag().equals("ARC")) {
          if (previous == null) throw new IOException("Arc without starting coordinate");
          Coordinate mid = coord(segment, "A1", "A2");
          if (segment.getattrvalue("R") != null)
            throw new IOException("Explicit-radius arc cannot yet be reliably indexed");
          double ax = mid.x - previous.x,
              ay = mid.y - previous.y,
              bx = end.x - previous.x,
              by = end.y - previous.y;
          double determinant = ax * by - ay * bx,
              scale = Math.max(Math.abs(ax * by), Math.abs(ay * bx));
          if (Math.abs(determinant) <= Math.ulp(Math.max(1.0, scale)) * 64)
            throw new IOException("Degenerate or numerically ambiguous arc");
          ArcSegment arc = new ArcSegment(previous, mid, end, 0.0);
          Envelope box = arc.computeEnvelopeInternal();
          if (box.isNull()
              || !Double.isFinite(box.getMinX())
              || !Double.isFinite(box.getMaxX())
              || !Double.isFinite(box.getMinY())
              || !Double.isFinite(box.getMaxY())) throw new IOException("Invalid arc envelope");
          // Exact decimal orientation and rational centre avoid a heuristic rounding budget.
          // The IOX envelope above remains an independent structural/finite check.
          exactArcEnvelope(previousObject, segment, env);
          include(env, mid);
        } else if (!segment.getobjecttag().equals("COORD"))
          throw new IOException("Unsupported line segment: " + segment.getobjecttag());
        include(env, end);
        previous = end;
        previousObject = segment;
      }
      return;
    }
    if (!Arrays.asList(
            "MULTICOORD", "POLYLINE", "MULTIPOLYLINE", "MULTISURFACE", "SURFACE", "BOUNDARY")
        .contains(tag)) throw new IOException("Unsupported geometry node: " + tag);
    for (int a = 0; a < o.getattrcount(); a++) {
      String name = o.getattrname(a);
      if (name.equals("lineattr")) continue;
      for (int i = 0; i < o.getattrvaluecount(name); i++) {
        IomObject child = o.getattrobj(name, i);
        if (child == null) throw new IOException("Invalid geometry member: " + name);
        walk(child, env);
      }
    }
  }
}
