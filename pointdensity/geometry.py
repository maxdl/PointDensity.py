#    Module      : Geometry.py
#    Date        : February 16, 2010
#    Description : Various computational geometry-related classes and functions
#
#    Copyright 2010 Max Larsson <m.d.larsson@medisin.uio.no>
#
#    This file is part of PointDensity.
#
#    PointDensity is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PointDensity is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PointDensity.  If not, see <http://www.gnu.org/licenses/>.

import math
import sys
import types

class Point(object):
    def __init__(self, x=None, y=None):
        if x != None:
            self.x = float(x)
        else:
            self.x = None
        if y != None:
            self.y = float(y)
        else:
            self.y = None
    
    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'
    
    def __nonzero__(self):  # true if both x and y are defined
        if self.x != None and self.y != None:
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
        return math.sqrt((self.x - q.x)**2 + (self.y - q.y)**2)
    
    def signedDistToLine(self, p, q):
        """ Calculate signed distance from self to the line defined by p and q. 
            Note that the function does not allow correct comparison of signs 
            between lines parallel to either axis and lines oriented otherwise. 
        """
        if p.y == q.y:
            return self.y - p.y
        elif p.x == q.x:
            return self.x - p.x
        else:
            a = 1 / (q.x - p.x)
            b = -1 / (q.y - p.y)
            c = p.y/ (q.y - p.y) - p.x / (q.x - p.x)
        return (a * self.x + b * self.y + c) / math.sqrt(a**2 + b**2)


    def isWithinPolygon(self, pol):
        """  Determine whether point p is inside polygon;
             Uses the crossing number method => works only with simple polygons.
        """
        if not pol:
            return None
        cn = 0
        for n in range(-1, len(pol) - 1):
            if (((pol[n].y <= self.y) and (pol[n+1].y > self.y))  
                or ((pol[n].y > self.y) and (pol[n+1].y) <= self.y)):
                if (lineIntersection(pol[n], pol[n+1], 
                    self, Point(self.x-1, self.y)).x > self.x):
                    cn += 1
        if cn % 2 == 1:
            return True
        else:
            return False
            
            
    def projectOnPath(self, path):
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
            v = Vec(path[n+1].x - path[n].x, path[n+1].y - path[n].y)
            d = abs(self.signedDistToLine(path[n], path[n+1]))
            if ((u.project(v).dot(v) >= 0) and (u.project(v).dist(Point(0,0)) 
                                                <= v.dist(Point(0,0))) 
                                           and d < mindist):
                mindist = d
                project = u.project(v) + path[n]
                seg0 = n
        if project:
            for n in range(1, len(path)-1):
                d = self.dist(path[n])
                if d < mindist:
                    mindist = d
                    project = path[n]
                    seg0 = n                            
        return project, seg0                
    
                
    def projectOnPathOrEndnode(self, path):
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
            v = Vec(path[n+1].x - path[n].x, path[n+1].y - path[n].y)        
            d = abs(self.signedDistToLine(path[n], path[n+1]))
            if ((u.project(v).dot(v) >= 0) and (u.project(v).dist(Point(0,0)) 
                                                <= v.dist(Point(0,0))) 
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

    def projectOnClosedPath(self, path):
        """ Determine the orthogonal projection of a point on a closed path;
            Return projection point and first node of the path segment on which
            the point projects.
        """
        mindist = float(sys.maxint)
        project = Point(None, None)
        seg0 = None
        for n in range(-1, len(path) - 1):
            u = Vec(self.x - path[n].x, self.y - path[n].y)
            v = Vec(path[n+1].x - path[n].x, path[n+1].y - path[n].y)
            d = abs(self.signedDistToLine(path[n], path[n+1]))
            if ((u.project(v).dot(v) >= 0) and (u.project(v).dist(Point(0,0))
                                                <= v.dist(Point(0,0)))
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
        #if seg0 == len(path):
        #    seg0 -= 1
        return project, seg0 
        
        
    def segmentCrossingNumber(self, path, refp, epsilon=1e-12):
        """ Return the number of times the line between a point p and and a 
            reference point refp crosses a segmented path (path)
        """
        cn = 0
        for n in range(0, len(path) - 1):
            d, t, u = lineIntersectionWithParams(self, refp, path[n], 
                                                 path[n+1])
            if d and (0 <= t <=1):  # is intersection between self and refp?
                if (0 <= u < 1):    # is intersection within path segment?
                    cn += 1
                elif abs(u-1) < epsilon: # if intersecting last segment node,
                    if (n == len(path)-2):   # count only if last path segment;
                        cn += 1              # else it would be counted twice 
                    # if the line tangents the node between two segments, i e 
                    # does not cross the PSM, regard it as no intersection; 
                    # thus, decrement cn by 1 now (net change will be 0)
                    elif (path[n].signedDistToLine(path[n+1], refp) *
                          path[n+2].signedDistToLine(path[n+1], refp)) > 0:
                        cn -= 1
                elif (u < 0 and n == 0) or (u > 1 and n == len(path)-2):
                    pass
        return cn        
        
    def distToSegment(self, path, n):
        """Calculate distance from the particle to segment n in path;
           First, determine if the orthogonal projection of the 
           particle on the path segment is between the nodes of 
           ("on") the segment - if not, return distance to the closest 
           node. Return distance and a flag which is set to 0 if "off"
           the first or last node of the path, otherwise to 1
        """
        u = Vec(self.x - path[n].x, self.y - path[n].y)
        v = Vec(path[n+1].x - path[n].x, path[n+1].y - path[n].y)
        if (u.project(v).dot(v) >= 0) and (u.project(v).dist(Point(0,0)) <= 
                                           v.dist(Point(0,0))):
               return True, abs(self.signedDistToLine(path[n], path[n+1]))
        else:        # So, not on segment.
            d0, d1 = abs(self.dist(path[n])), abs(self.dist(path[n+1]))
            if n == 0 and d0 < d1: 
                return False, d0
            elif n == len(path) - 2 and d1 < d0:  
                return False, d1
            else:
                return True, min(d0, d1)

    def perpendDistClosedPath(self, m, doNotCareIfOnOrOffSeg=True):
        """" Calculate distance from the point to a closed path m;
             negloc is a point defined to have a negative distance
             to the path; posloc is a point defined to have a positive
             distance to the path; if neither negloc nor posloc is
             defined, absolute distance is returned.
        """
        mindist = float(sys.maxint)
        for n in range(-1, len(m) - 1):
            if (m[n].x != -1) and (m[n+1].x != -1):
                on_this_seg, d = self.distToSegment(m, n)
                if d <= mindist:      # smallest distance so far...
                    mindist = d
                    if on_this_seg or doNotCareIfOnOrOffSeg:
                        on_M = True   # least distance and "on" segment (not
                                      # completely true; see distToSegment())
                    else:
                        on_M = False      # least distance but "off" segment
        if not on_M:
            return None # shouldn't happen because m is closed
        return mindist
# end of class Point

            
class Vec(Point):   
    def __rmul__(self, l): 
        """ Multiplication with scalar """
        if isinstance(l, types.IntType) or isinstance(l, types.FloatType):
            return Vec(l * self.x, l * self.y)
        else:
            raise TypeError, 'First operand not a scalar'
    
    def dot(self, v):
        " Dot product "     
        return (self.x * v.x + self.y * v.y)        
    
    def length(self):
        " Length of vector "
        return self.dist(Point(0, 0))
    
    def project(self, v):
        " Project self onto v " 
        return self.dot(v) / (v.x**2 + v.y**2) * v
# end of class Vec


class SegmentedPath(list):     
    def __init__(self, pointli=[]):
        try:
            self.extend([Point(p.x, p.y) for p in pointli])
        except (AttributeError, IndexError):
            raise TypeError, 'not a list of Point elements'
    
    def length(self):
        """Return length of a segmented path (assume path is open)"""
        if len(self) == 0:
            return 0.0
        L = 0.0
        for n in range(0, len(self) - 1):
            if (self[n].x != -1) and (self[n+1].x != -1):
                L = L + math.sqrt((self[n+1].x - self[n].x)**2 + 
                                  (self[n+1].y - self[n].y)**2)
        return L

    def perimeter(self):
        """Return length of a segmented path (assume path is closed)"""
        return self.length() + math.sqrt((self[-1].x - self[0].x)**2 + 
               (self[-1].y - self[0].y)**2)
        
    def centerPoint(self):      # assumes an open path
        """Return center point of a segmented path (assume path is open)"""
        if len(self) == 1:
            return Point(self[0].x, self[0].y)
        r = self.length() / 2
        L = 0.0
        for n in range(0, len(self) -  1):
            v = Vec(self[n+1].x - self[n].x, self[n+1].y - self[n].y)       
            L += v.length()
            if L >= r:
                break 
        return self[n] + ((v.length() - (L - r)) / v.length()) * v

    def signedArea(self):            
        """Return signed area of polygon (assume path is closed)"""
        if len(self) < 3:
            return 0.0
        a = (self[0].x - self[-1].x) * (self[-1].y + self[0].y) 
        for n in range(0, len(self) - 1):
            a += (self[n+1].x - self[n].x) * (self[n].y + self[n+1].y)
        return float(a) / 2
    
    def area(self):
        """Return area of polygon (assume path is closed)"""
        try:
            return abs(self.signedArea())
        except TypeError:
            return None  

    def contains(self, p):
        """  Determine whether point p is inside polygon (assumes closed path);
             Uses the crossing number method => works only with simple polygons.
        """
        if not p:
            return None
        return p.isWithinPolygon(self)
                           
    def centroid(self): 
        """Return centroid (center of gravity) of a polygon (assume closed 
           path and no crossing vertices)
        """
        Atot = self.signedArea()
        if Atot == 0:
            return self.centerPoint()
        cx, cy = 0., 0.
        for n in range(1, len(self)-1):
            At = SegmentedPath([self[0], self[n], self[n+1]]).signedArea() 
            cx += (self[0].x + self[n].x + self[n+1].x)*At  # weighted centroid 
            cy += (self[0].y + self[n].y + self[n+1].y)*At  # of triangle
        return Point(cx/(3*Atot), cy/(3*Atot))        

    def isOrientedToPath(self, path):
        p0, node0 = self[0].projectOnPathOrEndnode(path)
        pN, nodeN = self[-1].projectOnPathOrEndnode(path)
        if node0 > nodeN:
            return False
        elif node0 == nodeN:
            if p0 == pN and p0 in (path[0], path[-1]):
                pathseg = Vec(path[node0+1].x - path[node0].x, 
                              path[node0+1].y - path[node0].y)
                if (Vec(self[0].x, self[0].y).project(pathseg).length() <
                    Vec(self[-1].x, self[-1].y).project(pathseg).length()):
                        return False
            elif p0.dist(path[node0]) > pN.dist(path[node0]):
                return False
        return True
        
    def isOrientedToPath2(self, path):
        """ The above function seems a bit naive and convoluted, and does it 
            really work for all cases? 
            This version uses the fact that if the signed area of a polygon is 
            positive, then the orientation is counter-clockwise. Thus, simply
            compare the signs of the signed areas. 
            See comp.graphics.algorithms FAQ 2.07.
        """
        if self.signedArea() * path.signedArea() > 0:   # same sign?
            return True
        return False

    def orientToPath(self, path):
        if not self.isOrientedToPath(path):
            self.reverse()

    def checkOpenPath(self):
        """ Make sure that the open path does not intersect with itself
            Uses the naive algorithm of checking every segment against 
            every other segment.        
        """        
        for n1 in range(0, len(self)-3):
            for n2 in range(n1+2, len(self)-1):
                if segmentIntersection(self[n1], self[n1+1],
                                       self[n2], self[n2+1]):
                    return False
        return True
    
    def boundingBox(self):
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

    def isSimplePolygon(self):
        """ Makes sure that the closed path self is a simple polygon, 
            ie does not intersect with itself.
            Uses the naive algorithm of checking every segment against 
            every other segment.
        """        
        for n1 in range(-1, len(self)-1):
            for n2 in range(n1+1, len(self)-1):
                if self[n1] not in (self[n2-1], self[n2], self[n2+1]):
                    if segmentsIntersectOrCoincide(self[n1], self[n1+1],
                                                   self[n2], self[n2+1]):
                            return False
        return True
                                            

    def isWithinPolygon(self, path):
        """ Determines if self is completely within path. Assumes that
            both self and path are closed and simple.
        """
        for n in range(-1, len(self)-1):
            if not self[n].isWithinPolygon(path):
                return False
            for p in range(-1, len(path)-1):                    
                if segmentsIntersectOrCoincide(self[n], self[n+1],
                                               path[p], path[p+1]):
                    return False
        return True


    def overlapsPolygon(self, path):
        """ Determines whether polygon self and polygon path overlap
        """
        if self.isWithinPolygon(path) or path.isWithinPolygon(self):
            return True
        for n1 in range(-1, len(self)-1):
            for n2 in range(-1, len(path)-1):
                if segmentsIntersectOrCoincide(self[n1], self[n1+1],
                                               path[n2], path[n2+1]):
                    return True                                        
        return False
                                

# end of class SegmentedPath
        


def toMetricUnits(L, pixelwidth):
    """Scale length L (in pixels) to metric units, 
       using supplied pixel width
    """
    try:
        return L * pixelwidth  
    except TypeError:
        return L 
    
   
def toPixelUnits(L, pixelwidth):
    """Scales length L to pixel units, using supplied
       pixel width in arbitrary length units
    """
    try:            
        return L / pixelwidth
    except (TypeError, ZeroDivisionError):
        return L
     
     
def lineIntersectionWithParams(A, B, C, D):
    """Return intersection of infinite lines defined by AB and CD;
       also return parameters of AB (ie AB=A+t(B-A)) and CD 
       corresponding to the intersection
       Return (None, None), None, None if lines are parallel
       or coincident       
    """      
    denom = ((B.x - A.x) * (D.y - C.y) - (B.y - A.y) * (D.x - C.x))
    if denom == 0:      # if lines are parallel
        return Point(None, None), None, None 
    t = ((A.y - C.y) * (D.x - C.x) - (A.x - C.x) * (D.y - C.y)) / denom               
    u = ((A.y - C.y) * (B.x - A.x) - (A.x - C.x) * (B.y - A.y)) / denom
    return Point(A.x + t * (B.x - A.x), A.y + t * (B.y - A.y)), t, u

def lineIntersection(A, B, C, D):
    """Determine the intersection point between the infinite lines 
       defined by AB and CD
       Return (None, None) if lines are parallel or coincident 
    """
    return lineIntersectionWithParams(A, B, C, D)[0]
         
        
def segmentIntersection(A, B, C, D):
    """Determine the intersection point between the line segments AB and CD
       Return (None, None) if lines are parallel or coincident, or intersection 
       is on the extension of either segment
    """
    p, t, u = lineIntersectionWithParams(A, B, C, D)
    if p and (0 <= t <= 1) and (0 <= u <= 1):
        return p
    else:
        return Point(None, None)        

def segmentsCoincide(A, B, C, D):
    """
    """
    denominator = (B.x - A.x) * (D.y - C.y) - (B.y - A.y) * (D.x - C.x)
    numerator = (A.y - C.y) * (D.x - C.x) - (A.x - C.x) * (D.y - C.y)
    if denominator == numerator == 0:
        return True
    else:
        return False

def segmentsIntersectOrCoincide(A, B, C, D):
    """ Return True if segments intersect or coincide       
    """ 
    def overlapping():
        if ((C.x < A.x < D.x) or (C.x < B.x < D.x) or
           (C.y < A.y < D.y) or (C.y < B.y < D.y)  or
           (C in (A, B)) or (D in (A, B))):
            return True
        else: 
            return False

    denom = (B.x - A.x) * (D.y - C.y) - (B.y - A.y) * (D.x - C.x)
    tnumerator = (A.y - C.y) * (D.x - C.x) - (A.x - C.x) * (D.y - C.y)
    if denom == 0:     # if segments coincident or parallel
        if tnumerator == 0 and overlapping():  # if coincident and overlapping...
            return True
        else:                # ...else parallel or nonoverlapping
            return False    
    # now we know an intersection exists
    t = tnumerator / denom               
    u = ((A.y - C.y) * (B.x - A.x) - (A.x - C.x) * (B.y - A.y)) / denom
    if (0 <= t <=1) and (0 <= u <= 1):  # if intersection is not on extension
        return True                     # of either segment
    return False


def convexHull(pointli):
    """ Determine convex hull of the points in pointli.
        Uses the Gift wrapping algorithm.

        --- Non-functional! ---
    """
    return None
    if len(pointli) <= 3:
        return pointli
    p0 = pointli[0]
    for p in pointli[1:]:
        if (p.y < p0.y) or (p.y == p0.y and p.x < p0.x):
            p0 = p
    pointOnHull = p0
    hull = []
    for p1 in pointli:
        hull.append(pointOnHull)
        endpoint = p1
        for p2 in pointli:
            if (p2 == p1) or (p2 == pointOnHull) or (endpoint == pointOnHull):
                continue
            theta1 = math.atan2(endpoint.y - pointOnHull.y,
                                endpoint.x - pointOnHull.x)
            theta2 = math.atan2(p2.y - pointOnHull.y,
                                p2.x - pointOnHull.x)
            if theta2 > theta1:
                endpoint = p2
        pointOnHull = endpoint
        if pointOnHull == hull[0]:
            break
    return hull

def convexHullGraham(pointli):
    """ Determine the convex hull of the points in pointli.
        Uses Graham's algorithm after O'Rourke (1998).
        Returns a SegmentedPath.
    """

    def signedArea(A, B, C):
    # Computes the signed area of the triangle formed by A, B and C;
    # if this area < 0, then C is strictly left of the line A->B
        return SegmentedPath([A, B, C]).signedArea()

    def cmp(pi, pj):
        a = signedArea(p0, pi, pj)
        if a > 0:
            return -1
        elif a < 0:
            return 1
        else:   # if pi and pj are collinear with p0
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
            else:       # if pi and pj are coincident, delete whichever point
                        # occurs first in the list
                if pointli.index[pi] < pointli.index(pj):
                    pi.delete = True
                else:
                    pj.delete = True
                return 0

    # main function body
    if len(pointli) <= 2:   # if less than 3 points, the convex hull is equal
        return SegmentedPath(pointli[:])   # to pointli
    if len(pointli) == 3:             # if 3 points:
        if signedArea(*pointli) != 0: # if the points are not collinear,
            return SegmentedPath(pointli[:])         # return all points,
        else:                         # else only the end points
            return SegmentedPath([pointli[0], pointli[2]])
    # find the rightmost lowest point
    p0 = pointli[0]
    for p in pointli[1:]:
        if (p.y < p0.y) or (p.y == p0.y and p.x < p0.x):
            p0 = p
    # sort points with respect to angle between the vector p0->p and the x axis
    for p in pointli:
        p.delete = False
    sortedli = sorted([p for p in pointli if p != p0], cmp)
    # delete points marked for deletion (i.e., non-extreme points on the hull)
    for p in sortedli[:]:        # iterate over a copy of sortedli because we 
        if p.delete:             # will delete marked points in sortedli
            sortedli.remove(p)
    # core algorithm
    stack = [p0, sortedli[0]]
    i = 1    # we know that sortedli[0] is an extreme point on the hull
    while i < len(sortedli):
        # if sortedli[i] is to the left of the line between stack[-2] and
        # stack[-1], then sortedli[i] is provisionally on the hull and pushed
        # on the top of the stack
        if signedArea(stack[-2], stack[-1], sortedli[i]) > 0:
            stack.append(sortedli[i])
            i += 1
        else:
            stack.pop()
    return SegmentedPath(stack)

    
