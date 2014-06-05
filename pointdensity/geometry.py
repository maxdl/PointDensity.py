import math
import sys
import types


class Point(object):
    def __init__(self, x=None, y=None):
        if x is not None:
            self.x = float(x)
        else:
            self.x = None
        if y is not None:
            self.y = float(y)
        else:
            self.y = None

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'

    def __nonzero__(self):
        """ True if both x and y are defined """
        if self.x is not None and self.y is not None:
            return True
        else:
            return False

    def __eq__(self, p):
        if self.x == p.x and self.y == p.y:
            return True
        else:
            return False

    def __ne__(self, p):
        if self.x != p.x or self.y != p.y:
            return True
        else:
            return False

    def __sub__(self, q):
        return Point(self.x - q.x, self.y - q.y)

    def __add__(self, q):
        return Point(self.x + q.x, self.y + q.y)

    def dist(self, q):
        return math.sqrt((self.x - q.x) ** 2 + (self.y - q.y) ** 2)

    def signed_dist_to_line(self, p, q):
        """ Calculate signed distance from self to the line defined by
            p and q. Note that the function does not allow correct
            comparison of signs between lines parallel to either axis
            and lines oriented otherwise.
        """
        if p.y == q.y:
            return self.y - p.y
        elif p.x == q.x:
            return self.x - p.x
        else:
            a = 1 / (q.x - p.x)
            b = -1 / (q.y - p.y)
            c = p.y / (q.y - p.y) - p.x / (q.x - p.x)
        return (a * self.x + b * self.y + c) / math.sqrt(a ** 2 + b ** 2)

    def is_within_polygon(self, pol):
        """  Determine whether point p is inside polygon;
             Uses the crossing number method => works only with simple
             polygons.
        """
        if not pol:
            return None
        cn = 0
        for n in range(-1, len(pol) - 1):
            if ((pol[n].y <= self.y < pol[n + 1].y)
                    or ((pol[n].y > self.y) and pol[n + 1].y <= self.y)):
                if (line_intersection(pol[n], pol[n + 1], self,
                                      Point(self.x - 1, self.y)).x > self.x):
                    cn += 1
        if cn % 2 == 1:
            return True
        else:
            return False

    def project_on_path(self, path):
        """ Determine the orthogonal projection of a point on a segmented path;
            Return projection point and first node of the path segment on which
            the point projects. If no projection is possible, return
            Point(None, None), None.
        """
        mindist = float(sys.maxint)
        project = Point(None, None)
        seg0 = None
        for n in range(0, len(path) - 1):
            u = Vec(self.x - path[n].x, self.y - path[n].y)
            v = Vec(path[n + 1].x - path[n].x, path[n + 1].y - path[n].y)
            d = abs(self.signed_dist_to_line(path[n], path[n + 1]))
            if ((u.project(v).dot(v) >= 0) and (u.project(v).dist(Point(0, 0))
                                                <= v.dist(Point(0, 0)))
                    and d < mindist):
                mindist = d
                project = u.project(v) + path[n]
                seg0 = n
        if project:
            for n in range(1, len(path) - 1):
                d = self.dist(path[n])
                if d < mindist:
                    mindist = d
                    project = path[n]
                    seg0 = n
        return project, seg0

    def project_on_path_or_endnode(self, path):
        """ Determine the orthogonal projection of a point on a segmented path;
            Return projection point and first node of the path segment on which
            the point projects. If no projection is possible, choose nearest
            endpoint as projection.
        """
        mindist = float(sys.maxint)
        project = Point(None, None)
        seg0 = None
        for n in range(0, len(path) - 1):
            u = Vec(self.x - path[n].x, self.y - path[n].y)
            v = Vec(path[n + 1].x - path[n].x, path[n + 1].y - path[n].y)
            d = abs(self.signed_dist_to_line(path[n], path[n + 1]))
            if ((u.project(v).dot(v) >= 0) and (u.project(v).dist(Point(0, 0))
                                                <= v.dist(Point(0, 0)))
                    and d < mindist):
                mindist = d
                project = u.project(v) + path[n]
                seg0 = n
        for n in range(0, len(path)):
            d = self.dist(path[n])
            if d < mindist:
                mindist = d
                project = path[n]
                seg0 = n
        if seg0 == len(path):
            seg0 -= 1
        return project, seg0

    def project_on_closed_path(self, path):
        """ Determine the orthogonal projection of a point on a closed path;
            Return projection point and first node of the path segment on which
            the point projects.
        """
        mindist = float(sys.maxint)
        project = Point(None, None)
        seg0 = None
        for n in range(-1, len(path) - 1):
            u = Vec(self.x - path[n].x, self.y - path[n].y)
            v = Vec(path[n + 1].x - path[n].x, path[n + 1].y - path[n].y)
            d = abs(self.signed_dist_to_line(path[n], path[n + 1]))
            if ((u.project(v).dot(v) >= 0) and (u.project(v).dist(Point(0, 0))
                                                <= v.dist(Point(0, 0)))
                    and d < mindist):
                mindist = d
                project = u.project(v) + path[n]
                seg0 = n
        if project:
            for n in range(0, len(path)):
                d = self.dist(path[n])
                if d < mindist:
                    mindist = d
                    project = path[n]
                    seg0 = n
        for n in range(0, len(path)):
            d = self.dist(path[n])
            if d < mindist:
                mindist = d
                project = path[n]
                seg0 = n
        return project, seg0

    def lateral_dist(self, path):
        """ Determine lateral distance to center of path. If
            distance > 1, the projection of the point is on the
            extension of path.
        """
        subpath = SegmentedPath()
        # need node only
        foo, seg_path_center = \
            path.center_point().project_on_path_or_endnode(path)
        project, seg_project = self.project_on_path_or_endnode(path)
        subpath.extend([project, path.center_point()])
        if seg_path_center < seg_project:
            subpath.reverse()
        for n in range(min(seg_path_center, seg_project) + 1,
                       max(seg_path_center, seg_project)):
            subpath.insert(len(subpath) - 1, path[n])
        return subpath.length()

    def segment_crossing_number(self, path, refp):
        """ Return the number of times the line between a point p and a
            reference point refp crosses a segmented path (path)
        """
        cn = 0
        for n in range(0, len(path) - 1):
            d, t, u = line_intersection_with_params(self, refp, path[n],
                                                    path[n + 1])
            # is intersection between self and refp?
            if d and (0 <= t <= 1):
                # is intersection within path segment?
                if 0 <= u < 1:
                    cn += 1
                # if intersecting last segment node, count only if last
                # path segment; else it would be counted twice
                elif abs(u - 1) < sys.float_info.epsilon:
                    if n == len(path) - 2:
                        cn += 1
                    # if the line tangents the node between two
                    # segments, i e does not cross the path, regard it
                    # as no intersection; thus, decrement cn by 1 now
                    # (net change will be 0)
                    elif (path[n].signed_dist_to_line(path[n + 1], refp) *
                          path[n + 2].signed_dist_to_line(path[n + 1],
                                                          refp)) > 0:
                        cn -= 1
                elif (u < 0 and n == 0) or (u > 1 and n == len(path) - 2):
                    pass
        return cn

    def dist_to_segment(self, path, n):
        """Calculate distance from the point to segment n in path;
           First, determine if the orthogonal projection of the point
           on the path segment is between the nodes of ("on") the
           segment - if not, return distance to the closest node.
           Return distance and a flag which is set to 0 if "off" the
           first or last node of the path, otherwise to 1
        """
        u = Vec(self.x - path[n].x, self.y - path[n].y)
        v = Vec(path[n + 1].x - path[n].x, path[n + 1].y - path[n].y)
        if (u.project(v).dot(v) >= 0) and (u.project(v).dist(Point(0, 0)) <=
                                           v.dist(Point(0, 0))):
            return True, abs(self.signed_dist_to_line(path[n], path[n + 1]))
        else:  # So, not on segment.
            d0, d1 = abs(self.dist(path[n])), abs(self.dist(path[n + 1]))
            if n == 0 and d0 < d1:
                return False, d0
            elif n == len(path) - 2 and d1 < d0:
                return False, d1
            else:
                return True, min(d0, d1)

    def perpend_dist_closed_path(self, m, dont_care_if_on_or_off_seg=True):
        """" Calculate distance from the point to a closed path m
        """
        mindist = float(sys.maxint)
        on_m = False
        for n in range(-1, len(m) - 1):
            if (m[n].x != -1) and (m[n + 1].x != -1):
                on_this_seg, d = self.dist_to_segment(m, n)
                # smallest distance so far...
                if d <= mindist:
                    mindist = d
                    if on_this_seg or dont_care_if_on_or_off_seg:
                        # least distance and "on" segment (not
                        # completely true; see dist_to_segment())
                        on_m = True
                    else:
                        # least distance but "off" segment
                        on_m = False
        if not on_m:
            # shouldn't happen because m is closed
            return None
        return mindist

    def perpend_dist(self, m, negloc=None, posloc=None,
                     dont_care_if_on_or_off_seg=False):
        """" Calculate distance from the point to a path m; the
             polarity can be defined by negloc or posloc, which are
             points defined to have a negative and a positive distance
             to the path, respectively. If neither negloc nor posloc is
             defined, absolute distance is returned.
        """
        mindist = float(sys.maxint)
        on_m = False
        for n in range(0, len(m) - 1):
            if (m[n].x != -1) and (m[n + 1].x != -1):
                on_this_seg, d = self.dist_to_segment(m, n)
                if d <= mindist:
                    # smallest distance so far...
                    mindist = d
                    if on_this_seg or dont_care_if_on_or_off_seg:
                        # least distance and "on" segment (not
                        # completely true; see dist_to_segment())
                        on_m = True
                    else:
                        # least distance but "off" segment
                        on_m = False
        if not on_m:
            return None
        # If polarity (posloc or negloc) is defined, we say that points
        # on the positive side of the path have positive distances to
        # the path, while other points have negative distances. To
        # determine this, we count the number of path segments
        # dissected by the line between the particle and negloc
        # (posloc). Even (odd) number => the particle and negloc
        # (posloc) are on the same side of the path; odd number =>
        # different side.
        if (negloc is not None and
                self.segment_crossing_number(m, negloc) % 2 == 0):
            mindist = -mindist
        elif (posloc is not None and
              self.segment_crossing_number(m, posloc) % 2 != 0):
            mindist = -mindist
        return mindist

    def lateral_dist_to_point(self, p2, border):
        """ Determine lateral distance to a point p2 along profile
            border. Assume profile border is a closed path.
        """
        path = SegmentedPath()
        p2_project, p2_seg_project = p2.project_on_closed_path(border)
        project, seg_project = self.project_on_closed_path(border)
        path.extend([project, p2_project])
        if p2_seg_project < seg_project:
            path.reverse()
        for n in range(min(p2_seg_project, seg_project) + 1,
                       max(p2_seg_project, seg_project)):
            path.insert(len(path) - 1, border[n])
        length = path.length()
        return min(length, border.perimeter() - length)

# end of class Point


class Vec(Point):
    def __rmul__(self, l):
        """ Multiplication with scalar """
        if isinstance(l, types.IntType) or isinstance(l, types.FloatType):
            return Vec(l * self.x, l * self.y)
        else:
            raise TypeError('First operand not a scalar')

    def dot(self, v):
        """" Dot product """
        return self.x * v.x + self.y * v.y

    def length(self):
        """ Length of vector """
        return self.dist(Point(0, 0))

    def project(self, v):
        """ Project self onto v
        """
        return self.dot(v) / (v.x ** 2 + v.y ** 2) * v


# end of class Vec


class SegmentedPath(list):
    def __init__(self, pointli=None):
        if pointli is None:
            pointli = []
        try:
            self.extend([Point(p.x, p.y) for p in pointli])
        except (AttributeError, IndexError):
            raise TypeError('not a list of Point elements')

    def length(self):
        """Return length of a segmented path (assume path is open)"""
        if len(self) == 0:
            return 0.0
        length = 0.0
        for n in range(0, len(self) - 1):
            if (self[n].x != -1) and (self[n + 1].x != -1):
                length += math.sqrt((self[n + 1].x - self[n].x) ** 2 +
                                    (self[n + 1].y - self[n].y) ** 2)
        return length

    def perimeter(self):
        """Return length of a segmented path (assume path is closed)"""
        return self.length() + math.sqrt((self[-1].x - self[0].x) ** 2 +
                                         (self[-1].y - self[0].y) ** 2)

    def center_point(self):
        """ Return center point of a segmented path (assume path is
            open)
        """
        if len(self) == 1:
            return Point(self[0].x, self[0].y)
        r = self.length() / 2
        length = 0.0
        for n in range(0, len(self) - 1):
            v = Vec(self[n + 1].x - self[n].x, self[n + 1].y - self[n].y)
            length += v.length()
            if length >= r:
                break
        return self[n] + ((v.length() - (length - r)) / v.length()) * v

    def signed_area(self):
        """Return signed area of polygon (assume path is closed)"""
        if len(self) < 3:
            return 0.0
        a = (self[0].x - self[-1].x) * (self[-1].y + self[0].y)
        for n in range(0, len(self) - 1):
            a += (self[n + 1].x - self[n].x) * (self[n].y + self[n + 1].y)
        return float(a) / 2

    def area(self):
        """Return area of polygon (assume path is closed)"""
        try:
            return abs(self.signed_area())
        except TypeError:
            return None

    def contains(self, p):
        """  Determine whether point p is inside polygon (assumes closed path);
             Uses the crossing number method => works only with simple
             polygons.
        """
        if not p:
            return None
        return p.is_within_polygon(self)

    def centroid(self):
        """  Return centroid (center of gravity) of a polygon (assume closed
             path and no crossing vertices)
        """
        a_tot = self.signed_area()
        if a_tot == 0:
            return self.center_point()
        cx, cy = 0., 0.
        for n in range(1, len(self) - 1):
            a_t = SegmentedPath([self[0], self[n], self[n + 1]]).signed_area()
            # weighted centroid of triangle
            cx += (self[0].x + self[n].x + self[n + 1].x) * a_t
            cy += (self[0].y + self[n].y + self[n + 1].y) * a_t
        return Point(cx / (3 * a_tot), cy / (3 * a_tot))

    def is_oriented_to_path(self, path):
        """ Ok, so this is to investigate whether they both work
            I will test this for a while and then remove one version.
            Sorry for the overhead in the meantime :)
        """
        o1 = self.is_oriented_to_path1(path)
        o2 = self.is_oriented_to_path2(path)
        if o1 != o2:
            raise RuntimeError("is_oriented_to_path funcs do not match")
        return o1
        
    def is_oriented_to_path1(self, path):
        p0, node0 = self[0].project_on_path_or_endnode(path)
        pn, node_n = self[-1].project_on_path_or_endnode(path)
        if node0 > node_n:
            return False
        elif node0 == node_n:
            if p0 == pn and p0 in (path[0], path[-1]):
                pathseg = Vec(path[node0 + 1].x - path[node0].x,
                              path[node0 + 1].y - path[node0].y)
                if (Vec(self[0].x, self[0].y).project(pathseg).length() <
                        Vec(self[-1].x, self[-1].y).project(pathseg).length()):
                    return False
            elif p0.dist(path[node0]) > pn.dist(path[node0]):
                return False
        return True

    def is_oriented_to_path2(self, path):
        """ The above function seems a bit naive and convoluted, and does it
            really work for all cases?
            This version uses the fact that if the signed area of a polygon is
            positive, then the orientation is counter-clockwise. Thus, simply
            compare the signs of the signed areas.
            See comp.graphics.algorithms FAQ 2.07.
        """
        if self.signed_area() * path.signed_area() > 0:  # same sign?
            return True
        return False

    def orient_to_path(self, path):
        if not self.is_oriented_to_path(path):
            self.reverse()

    def check_open_path(self):
        """ Make sure that the open path does not intersect with itself
            Uses the naive algorithm of checking every segment against
            every other segment.
        """
        for n1 in range(0, len(self) - 3):
            for n2 in range(n1 + 2, len(self) - 1):
                if segment_intersection(self[n1], self[n1 + 1],
                                        self[n2], self[n2 + 1]):
                    return False
        return True

    def bounding_box(self):
        """ Determines bounding box of self.
        """
        hix = lox = self[0].x
        hiy = loy = self[0].y
        for n in self[1:]:
            if n.x > hix:
                hix = n.x
            elif n.x < lox:
                lox = n.x
            if n.y > hiy:
                hiy = n.y
            elif n.y < loy:
                loy = n.y
        return SegmentedPath([Point(lox, loy), Point(hix, loy),
                              Point(hix, hiy), Point(lox, hiy)])

    def is_simple_polygon(self):
        """ Makes sure that the closed path self is a simple polygon,
            ie does not intersect with itself.

            Uses the naive algorithm of checking every segment against
            every other segment.
        """
        for n1 in range(-1, len(self) - 1):
            for n2 in range(n1 + 1, len(self) - 1):
                if self[n1] not in (self[n2 - 1], self[n2], self[n2 + 1]):
                    if segments_intersect_or_coincide(self[n1], self[n1 + 1],
                                                      self[n2], self[n2 + 1]):
                        return False
        return True

    def is_within_polygon(self, path):
        """ Determines if self is completely within path. Assumes that
            both self and path are closed and simple.
        """
        for n in range(-1, len(self) - 1):
            if not self[n].is_within_polygon(path):
                return False
            for p in range(-1, len(path) - 1):
                if segments_intersect_or_coincide(self[n], self[n + 1],
                                                  path[p], path[p + 1]):
                    return False
        return True

    def overlaps_polygon(self, path):
        """ Determines whether polygon self and polygon path overlap.
        """
        if self.is_within_polygon(path) or path.is_within_polygon(self):
            return True
        for n1 in range(-1, len(self) - 1):
            for n2 in range(-1, len(path) - 1):
                if segments_intersect_or_coincide(self[n1], self[n1 + 1],
                                                  path[n2], path[n2 + 1]):
                    return True
        return False


# end of class SegmentedPath

def to_metric_units(l, pixelwidth):
    """Scale length l (in pixels) to metric units,
       using supplied pixel width
    """
    try:
        return l * pixelwidth
    except TypeError:
        return l


def to_pixel_units(l, pixelwidth):
    """Scales length l to pixel units, using supplied
       pixel width in arbitrary length units
    """
    try:
        return l / pixelwidth
    except (TypeError, ZeroDivisionError):
        return l


def line_intersection_with_params(a, b, c, d):
    """Return intersection of infinite lines defined by ab and cd;
       also return parameters of ab (ie ab=a+t(b-a)) and cd
       corresponding to the intersection
       Return (None, None), None, None if lines are parallel
       or coincident
    """
    denom = ((b.x - a.x) * (d.y - c.y) - (b.y - a.y) * (d.x - c.x))
    if denom == 0:  # if lines are parallel
        return Point(None, None), None, None
    t = ((a.y - c.y) * (d.x - c.x) - (a.x - c.x) * (d.y - c.y)) / denom
    u = ((a.y - c.y) * (b.x - a.x) - (a.x - c.x) * (b.y - a.y)) / denom
    return Point(a.x + t * (b.x - a.x), a.y + t * (b.y - a.y)), t, u


def line_intersection(a, b, c, d):
    """determine the intersection point between the infinite lines
       defined by ab and cd
       Return (None, None) if lines are parallel or coincident
    """
    return line_intersection_with_params(a, b, c, d)[0]


def segment_intersection(a, b, c, d):
    """Determine the intersection point between the line segments ab and cd
       Return (None, None) if lines are parallel or coincident, or intersection
       is on the extension of either segment
    """
    p, t, u = line_intersection_with_params(a, b, c, d)
    if p and (0 <= t <= 1) and (0 <= u <= 1):
        return p
    else:
        return Point(None, None)


def segments_coincide(a, b, c, d):
    """Return True if segments coincide"""
    denominator = (b.x - a.x) * (d.y - c.y) - (b.y - a.y) * (d.x - c.x)
    numerator = (a.y - c.y) * (d.x - c.x) - (a.x - c.x) * (d.y - c.y)
    if denominator == numerator == 0:
        return True
    else:
        return False


def segments_intersect_or_coincide(a, b, c, d):
    """Return True if segments intersect or coincide"""

    def overlapping():
        if ((c.x < a.x < d.x) or (c.x < b.x < d.x) or
                (c.y < a.y < d.y) or (c.y < b.y < d.y) or
                (c in (a, b)) or (d in (a, b))):
            return True
        else:
            return False

    denom = (b.x - a.x) * (d.y - c.y) - (b.y - a.y) * (d.x - c.x)
    tnumerator = (a.y - c.y) * (d.x - c.x) - (a.x - c.x) * (d.y - c.y)
    if denom == 0:  # if segments coincident or parallel
        if tnumerator == 0 and overlapping():  # if coincident and overlapping
            return True
        else:  # ...else parallel or nonoverlapping
            return False
    # now we know an intersection exists
    t = tnumerator / denom
    u = ((a.y - c.y) * (b.x - a.x) - (a.x - c.x) * (b.y - a.y)) / denom
    if (0 <= t <= 1) and (0 <= u <= 1):  # if intersection is not on extension
        return True  # of either segment
    return False


def convex_hull(pointli):
    """Determine the convex hull of the points in pointli.

    Uses Graham's algorithm after O'Rourke (1998).
    Returns a SegmentedPath.
    """

    def signed_area(a, b, c):
        # Computes the signed area of the triangle formed by a, b and c;
        # if this area < 0, then c is strictly left of the line a->b
        return SegmentedPath([a, b, c]).signed_area()

    def comp_func(pi, pj):
        a = signed_area(p0, pi, pj)
        if a > 0:
            return -1
        elif a < 0:
            return 1
        else:  # if pi and pj are collinear with p0
            # compare the length of the projections of p0->pi and p0-pj on the
            # x and y axes; if p0->pi shorter than p0->pj, then the projection
            # onto either of the axes should be shorter for this vector
            x = abs(pi.x - p0.x) - abs(pj.x - p0.x)
            y = abs(pi.y - p0.y) - abs(pj.y - p0.y)
            if x < 0 or y < 0:
                pi.delete = True
                return -1
            elif x > 0 or y > 0:
                pj.delete = True
                return 1
            else:  # if pi and pj are coincident, delete whichever point
                # occurs first in the list
                if pointli.index[pi] < pointli.index(pj):
                    pi.delete = True
                else:
                    pj.delete = True
                return 0

    # main function body
    if len(pointli) <= 2:  # if less than 3 points, the convex hull is equal
        return SegmentedPath(pointli[:])  # to pointli
    if len(pointli) == 3:  # if 3 points:
        if signed_area(*pointli) != 0:  # if the points are not collinear,
            return SegmentedPath(pointli[:])  # return all points,
        else:  # else only the end points
            return SegmentedPath([pointli[0], pointli[2]])
    # find the rightmost lowest point
    p0 = pointli[0]
    for p in pointli[1:]:
        if (p.y < p0.y) or (p.y == p0.y and p.x < p0.x):
            p0 = p
    # sort points with respect to angle between the vector p0->p and the x axis
    for p in pointli:
        p.delete = False
    sortedli = sorted([p for p in pointli if p != p0], comp_func)
    # delete points marked for deletion (i.e., non-extreme points on the hull)
    for p in sortedli[:]:  # iterate over a copy of sortedli because we
        if p.delete:  # will delete marked points in sortedli
            sortedli.remove(p)
    # core algorithm
    stack = [p0, sortedli[0]]
    i = 1  # we know that sortedli[0] is an extreme point on the hull
    while i < len(sortedli):
        # if sortedli[i] is to the left of the line between stack[-2] and
        # stack[-1], then sortedli[i] is provisionally on the hull and pushed
        # on the top of the stack
        if signed_area(stack[-2], stack[-1], sortedli[i]) > 0:
            stack.append(sortedli[i])
            i += 1
        else:
            stack.pop()
    return SegmentedPath(stack)
