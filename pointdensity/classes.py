#
#    Module      : classes.py
#    Description : Various class definitions; provides much core functionality
#
#    Copyright 2014 Max Larsson <max.larsson@liu.se>
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

import sys
import exceptions
import os.path
import random
import unicode_csv
import geometry
from fileIO import *
from stringconv import *


# Convenience functions
def dotProgress(x, linelength=120, char='.'):
    """ Simple progress indicator on sys.stdout
    """
    sys.stdout.write(char)
    if (x + 1) % linelength == 0:
        sys.stdout.write('\n')

#
# Classes
#
class Point(geometry.Point):
    def __init__(self, x=None, y=None, type=""):
        if isinstance(x, geometry.Point):
            geometry.Point.__init__(self, x.x, x.y)
        else:
            geometry.Point.__init__(self, x, y)
        self.skipped = False
        self.type = type
        self.cluster = None

    def determineStuff(self, parentli, profile, opt):
        if self.isWithinHole(profile.path):
            if self.type == "point":
                ProfileMessage(profile, "Discarding point at %s: Located "
                                        "within a profile hole" % self)
            self.skipped = True
            return
        self.distToPath = self.perpendDistClosedPath(profile.path)
        if not self.isWithinPolygon(profile.path):
            if self.distToPath > geometry.toPixelUnits(opt.shell_width,
                                              profile.pixelwidth):
                if self.type == "point":
                    ProfileMessage(profile, "Discarding point at %s: "
                                            "Located outside the shell" % self)
                self.skipped = True
                return
            self.distToPath = -self.distToPath
        self.isAssociatedWithPath = (abs(self.distToPath)
                                     <= geometry.toPixelUnits(opt.spatial_resolution,
                                                     profile.pixelwidth))
        self.isAssociatedWithProfile = (self.isWithinProfile(profile.path) or
                                        self.isAssociatedWithPath)



    def isWithinHole(self, path):
        """  Determine whether self is inside a profile hole
        """
        for h in path.holeli:
            if self.isWithinPolygon(h):
                return True
        return False


    def isWithinProfile(self, path):
        """  Determine whether self is inside profile, excluding holes
        """
        if (not self.isWithinPolygon(path)) or self.isWithinHole(path):
            return False
        return True



    def determineNearestNeighbour(self, pointli, opt):
        # Assumes that only valid (projectable, within shell etc) points are
        # in pointli
        self.nearestNeighbourDist = None
        self.nearestNeighbourPoint = Point()
        mindist = float(sys.maxint)
        for p in pointli:
            # I will instead exclude non-desired points from the supplied point
            # list *before* calling this function
            #if p is not self and p.isAssociatedWithProfile:
            if p is not self:
                d = self.dist(p)
                if d < mindist:
                    mindist = d
                    minp = p
        if not mindist < float(sys.maxint):
            return None
        else:
            self.nearestNeighbourDist = mindist
            self.nearestNeighbourPoint = minp
            return self.nearestNeighbourDist

    def determineNearestLateralNeighbour(self, pointli, profile, opt):
        # Assumes that only valid (projectable, within shell etc) points are
        # in pointli
        self.nearestLateralNeighbourDist = None
        self.nearestLateralNeighbourPoint = Point()
        mindist = float(sys.maxint)
        for p in pointli:
            if p is not self:
                d = self.lateralDistToPoint(p, profile.path)
                if d < mindist:
                    mindist = d
                    minp = p
        if not mindist < float(sys.maxint):
            return None
        else:
            self.nearestLateralNeighbourDist = mindist
            self.nearestLateralNeighbourPoint = minp
            return self.nearestLateralNeighbourDist


    def perpendDist(self, m, negloc=geometry.Point(None, None),
                    posloc=geometry.Point(None, None),
                    doNotCareIfOnOrOffSeg=False):
        """" Calculate distance from the point to an open path m;
             negloc is a point defined to have a negative distance
             to the path; posloc is a point defined to have a positive 
             distance to the path; if neither negloc nor posloc is 
             defined, absolute distance is returned.             
        """
        mindist = float(sys.maxint)
        on_M = False
        for n in range(0, len(m) - 1):
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
            return None
        # If polarity (posloc or negloc) is defined, we say that points
        # on the positive side of the path have positive distances to the 
        # path, while other points have negative distances. To 
        # determine this, we count the number of path segments 
        # dissected by the line between the point and negloc (posloc). 
        # Even (odd) number => the point and negloc (posloc) are on the same
        # same side of the path; odd number => different side.
        if negloc and self.segmentCrossingNumber(m, negloc) % 2 == 0:
            mindist = -mindist
        elif posloc and self.segmentCrossingNumber(m, posloc) % 2 != 0:
            mindist = -mindist
        return mindist

    def lateralDistToPoint(self, p2, border):
        """ Determine lateral distance to a point p2 along profile border.
        """
        path = geometry.SegmentedPath()
        p2_project, p2_seg_project = p2.projectOnClosedPath(border)
        project, seg_project = self.projectOnClosedPath(border)
        path.extend([project, p2_project])
        if p2_seg_project < seg_project:
            path.reverse()
        for n in range(min(p2_seg_project, seg_project) + 1,
                       max(p2_seg_project, seg_project)):
            path.insert(len(path)-1, border[n])
        L = path.length()
        return min(L, border.perimeter() - L)



class ProfileBorderData(geometry.SegmentedPath):
    def __init__(self, pointlist=[]):
        geometry.SegmentedPath.__init__(self, pointlist)
        self.holeli = []


    def addHole(self, pointlist=[]):
        self.holeli.append(pointlist)

    def area(self):
        """ Determine area of profile, excluding holes
        """
        return geometry.SegmentedPath.area(self) - sum([h.area() for h in self.holeli])

    def contains(self, p):
        """  Determine whether point p is inside profile border, 
             excluding holes
        """
        if not p:
            return None
        return p.isWithinProfile(self)

class PointList(list):
    def __init__(self, pointli, ptype):
        try:
            self.extend([Point(p.x, p.y, ptype) for p in pointli])
        except (AttributeError, IndexError):
            raise TypeError, 'not a list of Point elements'

class ClusterData(list):
    def __init__(self, pli=[]):
        try:
            self.extend([Point(p.x, p.y) for p in pli])
        except (AttributeError, IndexError):
            raise TypeError, 'not a particle list'
        self.convexHull = geometry.SegmentedPath()

    def lateralDistToCluster(self, c2, border):
        """ Determine lateral distance to a cluster c2 along profile border.
        """
        path = geometry.SegmentedPath()
        c2_project, c2_seg_project = c2.convexHull.centroid().projectOnClosedPath(border)
        project, seg_project = self.convexHull.centroid().projectOnClosedPath(border)
        path.extend([project, c2_project])
        if c2_seg_project < seg_project:
            path.reverse()
        for n in range(min(c2_seg_project, seg_project) + 1,
                       max(c2_seg_project, seg_project)):
            path.insert(len(path)-1, border[n])
        L = path.length()
        return min(L, border.perimeter() - L)


class ProfileData:
    def __init__(self, inputfn, opt):
        self.inputfn = inputfn
        self.outputfn = ""
        self.warnflag = False
        self.errflag = False

    def process(self, opt):
        """ Parse profile data from a file and determine distances
        """
        try:
            self.__parse(opt)
            self.__checkPaths()
            sys.stdout.write("Processing profile...\n")
            self.posloc = self.path.centroid()
            self.negloc = geometry.Point(None, None)
            if not self.posloc.isWithinPolygon(self.path):
                self.negloc = self.posloc
                self.posloc = geometry.Point(None, None)
            for p in self.pli:
                p.determineStuff(self.pli, self, opt)
            self.pli = [p for p in self.pli if not p.skipped]
            if opt.use_grid:
                for g in self.gridli:
                    g.determineStuff(self.gridli, self, opt)
                self.gridli = [g for g in self.gridli if not g.skipped]
            if opt.use_random:
                for r in self.randomli:
                    r.determineStuff(self.randomli, self, opt)
                self.randomli = [r for r in self.randomli if not r.skipped]
            self.getInterDistlis(opt)
            self.getClusters(opt)
            self.getMonteCarlo(opt)
            if opt.stop_requested:
                return
            sys.stdout.write("Done.\n")
        except ProfileError, (self, msg):
            sys.stdout.write("Error: %s\n" % msg)
            self.errflag = True

    def getMonteCarlo(self, opt):
        if opt.run_monte_carlo == False:
            self.mcli = []
        else:
            sys.stdout.write("Running Monte Carlo simulations...\n")
            self.mcli = self.runMonteCarlo(opt)

    def getClusters(self, opt):
        if not (opt.determine_clusters and opt.within_cluster_dist > 0):
            return
        sys.stdout.write("Determining clusters...\n")
        self.clusterli = self.determineClusters(self.pli, opt)
        self.processClusters(self.clusterli, opt)

    def getInterDistlis(self, opt):
        if not opt.determine_interpoint_dists:
            return
        if not True in [val for key, val in opt.interpoint_relations.items()
                                if "simulated" not in key]:
            return
        sys.stdout.write("Determining interpoint distances...\n")
        if opt.interpoint_relations["point - point"]:
            self.pp_distli, self.pp_latdistli = self.getSameInterpointDistances(opt, self.pli)
        if opt.use_random and opt.interpoint_relations["random - point"]:
            self.rp_distli, self.rp_latdistli = \
                    self.getInterpointDistances2(opt, self.randomli, self.pli)

    def getSameInterpointDistances(self, opt, pointli):
        dli = []
        latdli = []
        for i in range(0, len(pointli)):
            if opt.stop_requested:
                return [], []
            if opt.interpoint_dist_mode == 'all':
                for j in range(i + 1, len(pointli)):
                    if opt.interpoint_shortest_dist:
                        dli.append(pointli[i].dist(pointli[j]))
                    if opt.interpoint_lateral_dist:
                        latdli.append(pointli[i].lateralDistToPoint(pointli[j],
                                                                   self.path))
            elif opt.interpoint_dist_mode == 'nearest neighbour':
                if opt.interpoint_shortest_dist:
                    dli.append(pointli[i].determineNearestNeighbour(pointli,
                                                                    opt))
                if opt.interpoint_lateral_dist:
                    latdli.append(pointli[i].determineNearestLateralNeighbour(
                                                            pointli, self, opt))
        dli = [d for d in dli if d != None]
        latdli = [d for d in latdli if d != None]
        return dli, latdli


    def getInterpointDistances2(self, opt, pointli, pointli2=[]):
        dli = []
        latdli = []
        for i, p in enumerate(pointli):
            if opt.stop_requested:
                return [], []
            if opt.interpoint_dist_mode == 'all':
                for p2 in pointli2:
                    if opt.interpoint_shortest_dist:
                        dli.append(p.dist(p2))
                    if opt.interpoint_lateral_dist:
                        latdli.append(p.lateralDistToPoint(p2, self.path))
            elif opt.interpoint_dist_mode == 'nearest neighbour':
                if opt.interpoint_shortest_dist:
                    dli.append(p.determineNearestNeighbour(pointli2, opt))
                if opt.interpoint_lateral_dist:
                    latdli.append(p.determineNearestLateralNeighbour(pointli2,
                                                                     self, opt))
        dli = [d for d in dli if d is not None]
        latdli = [d for d in latdli if d is not None]
        return dli, latdli


    def runMonteCarlo(self, opt):

        def isValid(p):
            if p in mcli[n]["pli"]:
                return False
            if p.isWithinProfile(self.path):
                return True
            if p.isWithinHole(self.path):
                return False
            d = p.perpendDistClosedPath(self.path)
            if d is None:
                return False
            if (opt.monte_carlo_simulation_window == "profile" and not
                opt.monte_carlo_strict_location and
                (abs(d) < geometry.toPixelUnits(opt.spatial_resolution,
                                                self.pixelwidth))):
                    return True
            if (opt.monte_carlo_simulation_window == "profile + shell" and
                    abs(d) <= geometry.toPixelUnits(opt.shell_width,
                                                    self.pixelwidth)):
                return True
            return False

        pli = self.pli
        if opt.monte_carlo_simulation_window == "profile":
            if opt.monte_carlo_strict_location:
                numpoints = len([p for p in pli
                                    if p.isWithinProfile(self.path)])
            else:
                numpoints = len([p for p in pli if p.isAssociatedWithProfile])
        elif opt.monte_carlo_simulation_window == "profile + shell":
            numpoints = len(pli)  # this will suffice because points outside
                                  # shell have been discarded
        else:
            numpoints = len(pli)
        box = self.path.boundingBox()
        border = geometry.toPixelUnits(opt.shell_width, self.pixelwidth)
        mcli = []
        for n in range(0, opt.monte_carlo_runs):
            if opt.stop_requested:
                return []
            dotProgress(n)
            mcli.append({"pli": [],
                         "simulated - simulated": {"dist": [], "latdist": []},
                         "simulated - point": {"dist": [], "latdist": []},
                         "point - simulated": {"dist": [], "latdist": []},
                         "clusterli": []})
            for i in range(0, numpoints):
                while True:
                    x = random.randint(int(box[0].x - border),
                                       int(box[1].x + border) + 1)
                    y = random.randint(int(box[0].y - border),
                                       int(box[2].y + border) + 1)
                    p = Point(x, y)
                    if isValid(p):
                        break
                # escape the while loop when a valid simulated point is found
                mcli[n]["pli"].append(p)
            for p in mcli[n]["pli"]:
                p.determineStuff(mcli[n]["pli"], self, opt)
            if opt.determine_interpoint_dists:
                if opt.interpoint_relations["simulated - simulated"]:
                        distlis = self.getSameInterpointDistances(opt,
                                                                mcli[n]["pli"])
                        mcli[n]["simulated - simulated"]["dist"].append(distlis[0])
                        mcli[n]["simulated - simulated"]["latdist"].append(distlis[1])
                if opt.interpoint_relations["simulated - point"]:
                    distlis = self.getInterpointDistances2(opt, mcli[n]["pli"],
                                                           pli)
                    mcli[n]["simulated - point"]["dist"].append(distlis[0])
                    mcli[n]["simulated - point"]["latdist"].append(distlis[1])
                if opt.interpoint_relations["point - simulated"]:
                    distlis = self.getInterpointDistances2(opt, pli,
                                                           mcli[n]["pli"])
                    mcli[n]["point - simulated"]["dist"].append(distlis[0])
                    mcli[n]["point - simulated"]["latdist"].append(distlis[1])
        if opt.determine_clusters:
            for n, li in enumerate(mcli):
                dotProgress(n)
                mcli[n]["clusterli"] = self.determineClusters(li["pli"], opt)
                self.processClusters(mcli[n]["clusterli"], opt)
        sys.stdout.write("\n")
        return mcli


    def processClusters(self, clusterli, opt):
        for c in clusterli:
            if opt.stop_requested:
                return
            c.convexHull = geometry.convexHullGraham(c)
            c.distToPath = c.convexHull.centroid(
                                            ).perpendDistClosedPath(self.path)
        for c in clusterli:
            if opt.stop_requested:
                return
            c.nearestCluster = ClusterData()
            if len(clusterli) == 1:
                c.distToNearestCluster = -1
                return
            c.distToNearestCluster = sys.maxint
            for c2 in clusterli:
                if c2 != c:
                    d = c.lateralDistToCluster(c2, self.path)
                    if  d < c.distToNearestCluster:
                        c.distToNearestCluster = d
                        c.nearestCluster = c2


    def determineClusters(self, pointli, opt):
        """ Partition pointli into clusters; each cluster contains all points
            that are less than opt.within_cluster_dist from at least one
            other point in the cluster
        """
        clusterli = []
        for p1 in pointli:
            if opt.stop_requested:
                return []
            if p1.cluster:
                continue
            for p2 in pointli:
                if p1 != p2 and p1.dist(p2) <= geometry.toPixelUnits(
                                                    opt.within_cluster_dist,
                                                    self.pixelwidth):
                    if p2.cluster != None:
                        p1.cluster = p2.cluster
                        clusterli[p1.cluster].append(p1)
                        break
            else:
                p1.cluster = len(clusterli)
                clusterli.append(ClusterData([p1]))
        return clusterli



    def __parse(self, opt):
        """ Parse profile data from input file 
        """
        sys.stdout.write("\nParsing '%s':\n" % self.inputfn)
        li = readFile(self.inputfn)
        if not li:
            raise ProfileError(self, "Could not open input file")
        while li:
            s = li.pop(0).replace("\n","").strip()
            if s.split(" ")[0].upper() == "IMAGE":
                self.src_img = s.split(" ")[1]
            elif s.split(" ")[0].upper() == "PROFILE_ID":
                try:
                    self.ID = s.split(" ")[1]
                except IndexError:
                    self.ID = ''
            elif s.split(" ")[0].upper() == "COMMENT":
                try:
                    self.comment = s.split(" ", 1)[1]
                except IndexError:
                    self.comment = ''
            elif s.split(" ")[0].upper() == "PIXELWIDTH":
                try:
                    self.pixelwidth = float(s.split(" ")[1])
                    self.metric_unit = s.split(" ")[2]
                except (IndexError, ValueError):
                    raise ProfileError(self,
                                       "PIXELWIDTH is not a valid number")
            #elif s.split(" ")[0].upper() == "PROFILE_TYPE":
            #    try:
            #        self.profile_type = s.split(" ", 2)[2]
            #    except IndexError:
            #        pass
            elif s.upper() == "PROFILE_BORDER":
                self.path = ProfileBorderData(self.__getCoords(li, "path"))
            elif s.upper() == "PROFILE_HOLE":
                self.path.addHole(geometry.SegmentedPath(self.__getCoords(li,
                                                     "hole")))
            elif s.upper() in ("POINTS", "PARTICLES"):
                self.pli = PointList(self.__getCoords(li, "point"),
                                        "point")
            elif s.upper() == "RANDOM_POINTS":
                self.randomli = PointList(self.__getCoords(li, "random"),
                                             "random")
            elif s.upper() == "GRID":
                self.gridli = PointList(self.__getCoords(li, "grid"),
                                           "grid")
            elif s[0] != "#":          # unless specifically commented out
                ProfileWarning(self, "Unrecognized string '" + s +
                                     "' in input file")
        # Now, let's see if everything was found
        self.__checkParsedData(opt)

    def __checkParsedData(self, opt):
        """ See if the synapse data was parsed correctly, and print info on the
            parsed data to standard output.            
        """
        self.checkVarDefault(self, 'src_img', "Source image", "N/A")
        self.checkVarDefault(self, 'ID', "Profile ID", "N/A")
        self.checkVarDefault(self, 'comment', "Comment", "")
        self.checkVarVal(self, 'metric_unit', "Metric unit", 'metric_unit', opt)
        self.checkRequiredVar(self, 'pixelwidth', "Pixel width", self.metric_unit)
        #self.checkVarDefault('profile_type', "Profile type", "N/A")
        self.checkListVar(self, 'path', 'Profile border', 'nodes', 2)
        self.checkListVar(self, 'pli', 'Points', '', 0)
        self.checkTableVar(self.path, 'holeli', "Hole", "Holes", 0, 2)
        self.checkVarExists(self, 'gridli', "Grid", 'use_grid', opt)
        self.checkVarExists(self, 'randomli', "Random points", 'use_random', opt)


    def checkRequiredVar(self, parent, var_to_check, var_str, post_str):
        """ Confirm that parent has a required variable;
            else, raise ProfileError.
        """
        if not hasattr(parent, var_to_check):
            raise ProfileError(self, "%s not found in input file" % var_str)
        else:
            sys.stdout.write("  %s: %s %s\n"
                             % (var_str, parent.__dict__[var_to_check], post_str))

    def checkListLen(self, var, min_len):
        """ Returns True if var is a list and has at least min_len elements,
            else False
        """
        return isinstance(var, list) and len(var) >= min_len

    def checkListVar(self, parent, var_to_check, var_str, post_str, min_len):
        """ Confirms that parent has a var_to_check that is a list and has at
            least min_len elements; if var_to_check does not exist and
            min_len <= 0, assigns an empty list to var_to_check. Else, raise a
            ProfileError.
        """
        if not hasattr(parent, var_to_check):
            if min_len > 0:
                raise ProfileError(self, "%s not found in input file"
                                         % var_str_1)
            else:
                parent.__dict__[var_to_check] = []
        elif not self.checkListLen(parent.__dict__[var_to_check], min_len):
            raise ProfileError(self, "%s has too few coordinates" % var_str)
        if post_str != '':
            post_str = " " + post_str
        sys.stdout.write("  %s%s: %d\n"
                         % (var_str, post_str,
                            len(parent.__dict__[var_to_check])))

    def checkTableVar(self, parent, var_to_check, var_str_singular, var_str_plural,
                        min_len_1, min_len_2):
        """ Confirms that var_to_check exists, is a list and has at least
            min_len_1 elements, and that each of these has at least min_len_2
            subelements; if var_to_check does not exist and min_len_1 <= 0,
            assigns an empty list to var_to_check. Else, raise ProfileError.
        """
        if not hasattr(parent, var_to_check):
            if min_len_1 > 0:
                raise ProfileError(self, "%s not found in input file"
                                         % var_str_plural)
            else:
                parent.__dict__[var_to_check] = []
        elif not self.checkListLen(parent.__dict__[var_to_check], min_len_1):
            raise ProfileError(self, "Too few %s found in input file"
                               % var_str_plural.lower())
        else:
            for element in parent.__dict__[var_to_check]:
                if not self.checkListLen(element, min_len_2):
                    raise ProfileError(self, "%s has too few coordinates"
                                       % var_str_singular)
        sys.stdout.write("  %s: %d\n" % (var_str_plural,
                                         len(parent.__dict__[var_to_check])))


    def checkVarDefault(self, parent, var_to_check, var_str, default=""):
        """ Checks if var_to_check exists; if not, assign the default value
        to var_to_check. Never raises a ProfileError.
        """
        if not hasattr(parent, var_to_check):
            parent.__dict__[var_to_check] = default
        sys.stdout.write("  %s: %s\n" % (var_str,
                                         parent.__dict__[var_to_check]))


    def checkVarExists(self, parent, var_to_check, var_str, optflag, opt):
        """ Checks for consistency between profiles with respect to the
            existence of var_to_check (i.e., var_to_check must be present
            either in all profiles or in none).

            If optflag is not set (i.e., this is the first profile), then
            set optflag to True or False depending on the existence of
            var_to_check. If optflag is already set (for consequent profiles),
            var_to_check must (if optflag is True) or must not (if optflag is
            False) exist. If not so, raise ProfileError.
        """
        if not hasattr(opt, optflag):
            if hasattr(self, var_to_check):
                opt.__dict__[optflag] = True
            else:
                opt.__dict__[optflag] = False
        if opt.__dict__[optflag]:
            if hasattr(parent, var_to_check):
                sys.stdout.write("  %s: yes\n" % var_str)
            else:
                raise ProfileError(self, "%s not found in input file" % var_str)
        elif hasattr(parent, var_to_check):
            raise ProfileError(self, "%s found but not expected" % var_str)
        else:
            sys.stdout.write("  %s: no\n" % var_str)

    def checkVarVal(self, parent, var_to_check, var_str, optvar, opt):
        """ Checks for consistency between profiles with respect to the
            value of var_to_check (i.e., var_to_check must be present and
            have equal value in all profiles).

            If optvar is not set (i.e., this is the first profile), then
            set optflag to the value of var_to_check. If optvar is already set
            (for consequent profiles), the value of var_to_check must be equal
            to that of optvar. If not so, raise ProfileError.
        """
        if not hasattr(parent, var_to_check):
            raise ProfileError(self, "%s not found in input file" % var_str)
        if not hasattr(opt, optvar):
            opt.__dict__[optvar] = parent.__dict__[var_to_check]
        elif parent.__dict__[var_to_check] == opt.__dict__[optvar]:
            pass # really no point in pointing out that it's ok
            #sys.stdout.write("  %s: %s\n"
            #                 % (var_str, parent.__dict__[var_to_check]))
        else:
            raise ProfileError(self, "%s value '%s'  differs from the value "
                                     "specified ('%s') in the first input file"
                               % (var_str, parent.__dict__[var_to_check],
                                  opt.__dict__[optvar]))

    def __checkPaths(self):
        """ Make sure that profile border and holes do not intersect with
            themselves
        """
        def checkPath(path, s):
            for n1 in range(0, len(path)-3):
                for n2 in range(0, len(path)-1):
                    if n1 not in (n2, n2+1) and n1+1 not in (n2, n2+1):
                        if geometry.segmentIntersection(path[n1], path[n1+1],
                                               path[n2], path[n2+1]):
                            raise ProfileError(self,
                                            "%s invalid (crosses itself)" % s)
            return True

        checkPath(self.path, "Profile border")
        for path in self.path.holeli:
            checkPath(path, "Hole")
        for n, h in enumerate(self.path.holeli):
            if not h.isSimplePolygon():
                raise ProfileError(self,
                                   "Profile hole %d is not a simple polygon"
                                    % (n+1))
            for n2, h2 in enumerate(self.path.holeli[n+1:]):
                if h.overlapsPolygon(h2):
                    raise ProfileError(self,
                                       "Profile hole %d overlaps with hole %d "
                                       % (n+1, n+n2+2))
        sys.stdout.write("  Paths are ok.\n")


    def __getCoords(self, strli, coordType=""):
        """ Pop point coordinates from list strli.
            When an element of strli is not a valid point,
            a warning is issued.
        """
        pointli = []
        s = strli.pop(0).replace("\n","").replace(" ","").strip()
        while s != "END":
            try:
                p = geometry.Point(float(s.split(",")[0]), float(s.split(",")[1]))
                if pointli and (p == pointli[-1] or
                                (coordType in ('point', 'random')
                                 and p in pointli)):
                    sys.stdout.write("Duplicate %s coordinates %s: skipping "
                                     "2nd instance\n" % (coordType, p))
                else:
                    pointli.append(p)
            except ValueError:
                if s[0] != "#":
                    ProfileWarning(self, "'%s' not valid %s coordinates"
                                   % (s, coordType))
                else:
                    pass
            s = strli.pop(0).replace("\n","").strip()
        # For some reason, sometimes the endnodes have the same coordinates;
        # in that case, delete the last endnode to avoid division by zero
        if (len(pointli) > 1) and (pointli[0] == pointli[-1]):
            del pointli[-1]
        return pointli

    def __saveResults(self, opt):
        """ Output results from a single synapse to file
        """

        def m(x):
            try:
                return toMetricUnits(x, self.pixelwidth)
            except ZeroDivisionError:
                return None

        def m2(x):
            try:
                return toMetricUnits(x, self.pixelwidth**2) # for area units...
            except ZeroDivisionError:
                return None

        def fwrite(*args):
            f.writerow(args)


        try:
            self.outputfn = os.path.join(opt.output_dir,
                                         opt.output_filename_suffix +
                                         os.path.basename(self.inputfn)
                                         + opt.output_filename_ext)
            if (os.path.exists(self.outputfn) and
                opt.action_if_output_file_exists == 'enumerate'):
                    self.outputfn = enumFilename(self.outputfn, 2)
            sys.stdout.write("Writing to '%s'...\n" % self.outputfn)
            if opt.output_file_format == "csv":
                csv_format = { 'dialect' : 'excel', 'lineterminator' : '\n'}
                if opt.csv_delimiter == 'tab':
                    csv_format['delimiter'] = '\t'
                f = unicode_csv.writer(file(self.outputfn, "w"),
                                        **opt.csv_format)
            elif opt.output_file_format == 'excel':
                import xls
                f = xls.writer(self.outputfn)
            fwrite("Table 1. Profile-centric data")
            fwrite("Source image:", self.src_img)
            fwrite("Profile ID:", self.ID)
            fwrite("Comment:", self.comment)
            fwrite("Pixel width:", tostr(float(self.pixelwidth), 2),
                                   self.metric_unit)
            fwrite("Number of points (total):", len(self.pli))
            fwrite("Number of random points (total):", len(self.randomli))
            fwrite("Table 2. Point-centric data")
            columnheadings = ["Point number (as appearing in input file)",
                              "Point coordinates (in pixels)"]
            fwrite(*columnheadings)
            f.writerows([[n+1,
                          str(p)]
                          for n, p in enumerate(self.pli)])
            fwrite("Table 3. Random point-centric data")
            columnheadings = ["Random point number (as appearing in input file)",
                              "Random point coordinates (in pixels)"]
            fwrite(*columnheadings)
            f.writerows([[n+1,
                          str(r)]
                          for n, r in enumerate(self.randomli)])
            f.close()
        except IOError:
            raise ProfileError(self, "Unable to write to file '%s'"
                               % self.outputfn)
            return 0
        sys.stdout.write("Done.\n")
        return 1


# end of class Profile        

class OptionData:
    def __init__(self):
        self.infileList = []
        self.spatial_resolution = 25
        self.shell_width = 0   # Skip points farther than this from profile
        self.outputs = {'profile summary': True, 'point summary': True,
                        'random summary': True, 'session summary': True,
                        'individual profiles': False}
        self.output_file_format = "excel"
        self.output_filename_ext = ".xls"
        self.input_filename_ext = ".pd"
        self.output_filename_suffix = ''
        self.output_filename_other_suffix = ''
        self.output_filename_date_suffix = True
        self.csv_delimiter = "comma"
        self.action_if_output_file_exists = 'overwrite'
        self.output_dir = ''
        self.determine_clusters = False
        self.within_cluster_dist = 50
        self.run_monte_carlo = False
        self.monte_carlo_runs = 99
        self.monte_carlo_simulation_window = 'profile'
        self.monte_carlo_strict_location = False
        self.determine_interpoint_dists = False
        self.interpoint_dist_mode = 'nearest neighbour'
        self.interpoint_relations = {'point - point': True,
                                    'random - point': True,
                                    'point - simulated': False,
                                    'simulated - point': False,
                                    'simulated - simulated': False}
        self.interpoint_shortest_dist = True
        self.interpoint_lateral_dist = False

# end of class OptionData

class ProfileError(exceptions.Exception):
    def __init__(self, profile, msg):
        self.args = (profile, msg + ".")

def ProfileWarning(profile, msg):
    """ Issue a warning
    """
    sys.stdout.write("Warning: %s.\n" % msg)
    profile.warnflag = True

def ProfileMessage(profile, msg):
    """ Show a message
    """
    sys.stdout.write("%s.\n" % msg)
