import sys
import exceptions
import os.path
import random
import unicode_csv
import geometry
import file_io
import stringconv


# Convenience functions
def dot_progress(x, linelength=120, char='.'):
    """Simple progress indicator on sys.stdout"""
    sys.stdout.write(char)
    if (x + 1) % linelength == 0:
        sys.stdout.write('\n')


#
# Classes
#


class Point(geometry.Point):
    def __init__(self, x=None, y=None, ptype=""):
        if isinstance(x, geometry.Point):
            geometry.Point.__init__(self, x.x, x.y)
        else:
            geometry.Point.__init__(self, x, y)
        self.skipped = False
        self.ptype = ptype
        self.cluster = None
        self.dist_to_path = None
        self.is_within_profile = None
        self.is_associated_with_path = None
        self.is_associated_with_profile = None
        self.nearest_neighbour_dist = None
        self.nearest_neighbour_point = geometry.Point()
        self.nearest_lateral_neighbour_dist = None
        self.nearest_lateral_neighbour_point = geometry.Point()

    def determine_stuff(self, profile):
        if self.__is_within_hole(profile.path):
            if self.ptype == "point":
                profile_message("Discarding point at %s: Located "
                                "within a profile hole" % self)
            self.skipped = True
            profile.nskipped[self.ptype] += 1
            return
        self.dist_to_path = self.perpend_dist_closed_path(profile.path)
        if not self.is_within_polygon(profile.path):
            if self.dist_to_path > geometry.to_pixel_units(
                    profile.opt.shell_width,
                    profile.pixelwidth):
                if self.ptype == "point":
                    profile_message("Discarding point at %s: "
                                    "Located outside the shell" % self)
                self.skipped = True
                profile.nskipped[self.ptype] += 1
                return
            self.dist_to_path = -self.dist_to_path
        self.is_within_profile = self.__is_within_profile(profile.path)
        self.is_associated_with_path = (abs(self.dist_to_path)
                                        <= geometry.to_pixel_units(
                                        profile.opt.spatial_resolution,
                                        profile.pixelwidth))
        self.is_associated_with_profile = (self.is_within_profile
                                           or self.is_associated_with_path)

    def __is_within_hole(self, path):
        """Determine if self is inside a profile hole."""
        for h in path.holeli:
            if self.is_within_polygon(h):
                return True
        return False

    def __is_within_profile(self, path):
        """Determine if self is inside profile, excluding holes."""
        if (not self.is_within_polygon(path)) or self.__is_within_hole(path):
            return False
        return True

    def get_nearest_neighbour(self, pointli):
        """Determine distance to nearest neighbour."""
        # Assumes that only valid (projectable, within shell etc) points
        # are in pointli
        mindist = float(sys.maxint)
        #minp = Point()
        for p in pointli:
            # I will instead exclude non-desired points from the
            # supplied point list *before* calling this function
            #if p is not self and p.isAssociatedWithProfile:
            if p is not self:
                d = self.dist(p)
                if d < mindist:
                    mindist = d
                    #minp = p
        if not mindist < float(sys.maxint):
            return None
        else:
            self.nearest_neighbour_dist = mindist
            #self.nearest_neighbour_point = minp
            return self.nearest_neighbour_dist

    def get_nearest_lateral_neighbour(self, pointli, profile):
        """Determine distance along profile border to nearest neighbour."""
        # Assumes that only valid (projectable, within shell etc) points
        # are in pointli
        mindist = float(sys.maxint)
        minp = Point()
        for p in pointli:
            if p is not self:
                d = self.lateral_dist_to_point(p, profile.path)
                if d < mindist:
                    mindist = d
                    minp = p
        if not mindist < float(sys.maxint):
            return None
        else:
            self.nearest_lateral_neighbour_dist = mindist
            self.nearest_lateral_neighbour_point = minp
            return self.nearest_lateral_neighbour_dist


class ProfileBorderData(geometry.SegmentedPath):
    def __init__(self, pointlist=None):
        if pointlist is None:
            pointlist = []
        geometry.SegmentedPath.__init__(self, pointlist)
        self.holeli = []

    def add_hole(self, pointlist=None):
        if pointlist is None:
            pointlist = []
        self.holeli.append(pointlist)

    def area(self):
        """Determine area of profile, excluding holes"""
        tot_hole_area = sum([h.area() for h in self.holeli])
        return geometry.SegmentedPath.area(self) - tot_hole_area

    def contains(self, p):
        """Determine if a point is inside profile, excluding holes."""
        if not p:
            return None
        return p.is_within_profile(self)


class PointList(list):
    def __init__(self, pointli, ptype):
        try:
            self.extend([Point(p.x, p.y, ptype) for p in pointli])
        except (AttributeError, IndexError):
            raise TypeError('not a list of Point elements')


class ClusterData(list):
    def __init__(self, pointli=None):
        if pointli is None:
            pointli = []
        try:
            self.extend([Point(p.x, p.y) for p in pointli])
        except (AttributeError, IndexError):
            raise TypeError('not a point list')
        self.convex_hull = geometry.SegmentedPath()

    def lateral_dist_to_cluster(self, c2, border):
        """Determine lateral distance to a cluster c2 along profile
        border.
        """
        path = geometry.SegmentedPath()
        c2_project, c2_seg_project = c2.convex_hull.centroid().\
            project_on_closed_path(border)
        project, seg_project = self.convex_hull.centroid().\
            project_on_closed_path(border)
        path.extend([project, c2_project])
        if c2_seg_project < seg_project:
            path.reverse()
        for n in range(min(c2_seg_project, seg_project) + 1,
                       max(c2_seg_project, seg_project)):
            path.insert(len(path) - 1, border[n])
        length = path.length()
        return min(length, border.perimeter() - length)


class ProfileData:
    def __init__(self, inputfn, opt):
        self.inputfn = inputfn
        self.outputfn = ""
        self.opt = opt
        self.pli = []
        self.gridli = []
        self.randomli = []
        self.mcli = []
        self.clusterli = []
        self.pp_distli, self.pp_latdistli = [], []
        self.rp_distli, self.rp_latdistli = [], []
        self.nskipped = {"point": 0, "random": 0, "grid": 0}
        self.comment = ""
        self.pixelwidth = None
        self.metric_unit = ""
        self.posloc = geometry.Point()
        self.negloc = geometry.Point()
        self.warnflag = False
        self.errflag = False

    def process(self):
        """ Parse profile data from a file and determine distances
        """
        try:
            self.__parse()
            self.__check_paths()
            sys.stdout.write("Processing profile...\n")
            self.posloc = self.path.centroid()
            if not self.posloc.is_within_polygon(self.path):
                self.negloc = self.posloc
                self.posloc = geometry.Point()
            for p in self.pli:
                p.determine_stuff(self)
            self.pli = [p for p in self.pli if not p.skipped]
            if self.opt.use_grid:
                for g in self.gridli:
                    g.determine_stuff(self)
                self.gridli = [g for g in self.gridli if not g.skipped]
            if self.opt.use_random:
                for r in self.randomli:
                    r.determine_stuff(self)
                self.randomli = [r for r in self.randomli if not r.skipped]
            for ptype in ("point", "random", "grid"):
                if ((ptype == "random" and not self.opt.use_random) or
                        (ptype == "grid" and not self.opt.use_grid)):
                    continue
                ptypestr = ("particles"
                            if ptype == "point" else ptype + " points")
                sys.stdout.write("  Number of %s skipped: %d\n"
                                 % (ptypestr, self.nskipped[ptype]))
            self.get_interdistlis()
            self.get_clusters()
            self.get_monte_carlo()
            if self.opt.stop_requested:
                return
            sys.stdout.write("Done.\n")
        except ProfileError, (self, msg):
            sys.stdout.write("Error: %s\n" % msg)
            self.errflag = True

    def get_monte_carlo(self):
        if self.opt.run_monte_carlo:
            sys.stdout.write("Running Monte Carlo simulations...\n")
            self.mcli = self.run_monte_carlo()

    def get_clusters(self):
        if not (self.opt.determine_clusters and
                self.opt.within_cluster_dist > 0):
            return
        sys.stdout.write("Determining clusters...\n")
        self.clusterli = self.determine_clusters(self.pli)
        self.process_clusters(self.clusterli)

    def get_interdistlis(self):
        if not self.opt.determine_interpoint_dists:
            return
        if not True in [val for key, val in
                        self.opt.interpoint_relations.items()
                        if "simulated" not in key]:
            return
        sys.stdout.write("Determining interpoint distances...\n")
        if self.opt.interpoint_relations["point - point"]:
            self.pp_distli, self.pp_latdistli = \
                self.get_same_interpoint_distances(self.pli)
        if self.opt.use_random and self.opt.interpoint_relations["random - "
                                                                 "point"]:
            self.rp_distli, self.rp_latdistli = \
                self.get_interpoint_distances2(self.randomli, self.pli)

    def get_same_interpoint_distances(self, pointli):
        dli = []
        latdli = []
        for i in range(0, len(pointli)):
            if self.opt.stop_requested:
                return [], []
            if self.opt.interpoint_dist_mode == 'all':
                for j in range(i + 1, len(pointli)):
                    if self.opt.interpoint_shortest_dist:
                        dli.append(pointli[i].dist(pointli[j]))
                    if self.opt.interpoint_lateral_dist:
                        latdli.append(pointli[i].
                                      lateral_dist_to_point(pointli[j],
                                                            self.path))
            elif self.opt.interpoint_dist_mode == 'nearest neighbour':
                if self.opt.interpoint_shortest_dist:
                    dli.append(pointli[i].get_nearest_neighbour(pointli,
                                                                self.opt))
                if self.opt.interpoint_lateral_dist:
                    latdli.append(pointli[i].get_nearest_lateral_neighbour(
                        pointli, self, self.opt))
        dli = [d for d in dli if d is not None]
        latdli = [d for d in latdli if d is not None]
        return dli, latdli

    def get_interpoint_distances2(self, pointli, pointli2=None):
        if pointli2 is None:
            pointli2 = []
        dli = []
        latdli = []
        for i, p in enumerate(pointli):
            if self.opt.stop_requested:
                return [], []
            if self.opt.interpoint_dist_mode == 'all':
                for p2 in pointli2:
                    if self.opt.interpoint_shortest_dist:
                        dli.append(p.dist(p2))
                    if self.opt.interpoint_lateral_dist:
                        latdli.append(p.lateral_dist_to_point(p2, self.path))
            elif self.opt.interpoint_dist_mode == 'nearest neighbour':
                if self.opt.interpoint_shortest_dist:
                    dli.append(p.get_nearest_neighbour(pointli2))
                if self.opt.interpoint_lateral_dist:
                    latdli.append(p.get_nearest_lateral_neighbour(pointli2,
                                                                  self))
        dli = [d for d in dli if d is not None]
        latdli = [d for d in latdli if d is not None]
        return dli, latdli

    def run_monte_carlo(self):

        def isvalid(pt):
            if pt in mcli[n]["pli"]:
                return False
            if pt.is_within_profile(self.path):
                return True
            if pt.__is_within_hole(self.path):
                return False
            d = pt.perpend_dist_closed_path(self.path)
            if d is None:
                return False
            if (self.opt.monte_carlo_simulation_window == "profile" and not
                self.opt.monte_carlo_strict_location and
                    (abs(d) < geometry.to_pixel_units(
                     self.opt.spatial_resolution, self.pixelwidth))):
                return True
            if (self.opt.monte_carlo_simulation_window == "profile + shell" and
                abs(d) <= geometry.to_pixel_units(self.opt.shell_width,
                                                  self.pixelwidth)):
                return True
            return False

        pli = self.pli
        if self.opt.monte_carlo_simulation_window == "profile":
            if self.opt.monte_carlo_strict_location:
                numpoints = len([p for p in pli
                                 if p.is_within_profile(self.path)])
            else:
                numpoints = len([p for p in pli if p.isAssociatedWithProfile])
        elif self.opt.monte_carlo_simulation_window == "profile + shell":
            numpoints = len(pli)  # this will suffice because points outside
            # shell have been discarded
        else:
            numpoints = len(pli)
        box = self.path.bounding_box()
        border = geometry.to_pixel_units(self.opt.shell_width, self.pixelwidth)
        mcli = []
        for n in range(0, self.opt.monte_carlo_runs):
            if self.opt.stop_requested:
                return []
            dot_progress(n)
            mcli.append({"pli": [],
                         "simulated - simulated": {"dist": [], "latdist": []},
                         "simulated - point": {"dist": [], "latdist": []},
                         "point - simulated": {"dist": [], "latdist": []},
                         "clusterli": []})
            p = Point()
            for i in range(0, numpoints):
                while True:
                    x = random.randint(int(box[0].x - border),
                                       int(box[1].x + border) + 1)
                    y = random.randint(int(box[0].y - border),
                                       int(box[2].y + border) + 1)
                    p = Point(x, y)
                    if isvalid(p):
                        break
                # escape the while loop when a valid simulated point is found
                mcli[n]["pli"].append(p)
            for p in mcli[n]["pli"]:
                p.determine_stuff(mcli[n]["pli"], self)
            if self.opt.determine_interpoint_dists:
                if self.opt.interpoint_relations["simulated - simulated"]:
                    distlis = self.get_same_interpoint_distances(mcli[n]["pli"])
                    mcli[n]["simulated - simulated"]["dist"].append(distlis[0])
                    mcli[n]["simulated - simulated"]["latdist"].append(
                        distlis[1])
                if self.opt.interpoint_relations["simulated - point"]:
                    distlis = self.get_interpoint_distances2(mcli[n]["pli"],
                                                             pli)
                    mcli[n]["simulated - point"]["dist"].append(distlis[0])
                    mcli[n]["simulated - point"]["latdist"].append(distlis[1])
                if self.opt.interpoint_relations["point - simulated"]:
                    distlis = self.get_interpoint_distances2(pli,
                                                             mcli[n]["pli"])
                    mcli[n]["point - simulated"]["dist"].append(distlis[0])
                    mcli[n]["point - simulated"]["latdist"].append(distlis[1])
        if self.opt.determine_clusters:
            for n, li in enumerate(mcli):
                dot_progress(n)
                mcli[n]["clusterli"] = self.determine_clusters(li["pli"])
                self.process_clusters(mcli[n]["clusterli"])
        sys.stdout.write("\n")
        return mcli

    def process_clusters(self, clusterli):
        for c in clusterli:
            if self.opt.stop_requested:
                return
            c.convex_hull = geometry.convex_hull(c)
            hull_centroid = c.convex_hull.centroid()
            c.dist_to_path = hull_centroid.perpend_dist_closed_path(self.path)
        for c in clusterli:
            if self.opt.stop_requested:
                return
            c.nearestCluster = ClusterData()
            if len(clusterli) == 1:
                c.distToNearestCluster = -1
                return
            c.distToNearestCluster = sys.maxint
            for c2 in clusterli:
                if c2 != c:
                    d = c.lateral_dist_to_cluster(c2, self.path)
                    if d < c.distToNearestCluster:
                        c.distToNearestCluster = d
                        c.nearestCluster = c2

    def determine_clusters(self, pointli):
        """ Partition pointli into clusters; each cluster contains all points
            that are less than opt.within_cluster_dist from at least one
            other point in the cluster
        """
        clusterli = []
        for p1 in pointli:
            if self.opt.stop_requested:
                return []
            if p1.cluster:
                continue
            for p2 in pointli:
                if p1 != p2 and p1.dist(p2) <= geometry.to_pixel_units(
                        self.opt.within_cluster_dist,
                        self.pixelwidth):
                    if p2.cluster is not None:
                        p1.cluster = p2.cluster
                        clusterli[p1.cluster].append(p1)
                        break
            else:
                p1.cluster = len(clusterli)
                clusterli.append(ClusterData([p1]))
        return clusterli

    def __parse(self):
        """Parse profile data from input file."""
        sys.stdout.write("\nParsing '%s':\n" % self.inputfn)
        li = file_io.read_file(self.inputfn)
        if not li:
            raise ProfileError(self, "Could not open input file")
        while li:
            s = li.pop(0).replace("\n", "").strip()
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
                self.path = ProfileBorderData(self.__get_coords(li, "path"))
            elif s.upper() == "PROFILE_HOLE":
                self.path.add_hole(geometry.SegmentedPath(
                    self.__get_coords(li, "hole")))
            elif s.upper() in ("POINTS", "PARTICLES"):
                self.pli = PointList(self.__get_coords(li, "point"), "point")
            elif s.upper() == "RANDOM_POINTS":
                self.randomli = PointList(self.__get_coords(li, "random"),
                                          "random")
            elif s.upper() == "GRID":
                self.gridli = PointList(self.__get_coords(li, "grid"),
                                        "grid")
            elif s[0] != "#":  # unless specifically commented out
                profile_warning(self, "Unrecognized string '" + s +
                                "' in input file")
        # Now, let's see if everything was found
        self.__check_parsed_data()

    def __check_parsed_data(self):
        """See if the profile data was parsed correctly, and print info
        on the parsed data to stdout.
        """
        self.check_var_default(self, 'src_img', "Source image", "N/A")
        self.check_var_default(self, 'ID', "Profile ID", "N/A")
        self.check_var_default(self, 'comment', "Comment", "")
        self.check_var_val(self, 'metric_unit', "Metric unit", 'metric_unit')
        self.check_required_var(self, 'pixelwidth', "Pixel width",
                                self.metric_unit)
        #self.check_var_default('profile_type', "Profile type", "N/A")
        self.check_list_var(self, 'path', 'Profile border', 'nodes', 2)
        self.check_list_var(self, 'pli', 'Points', '', 0)
        self.check_table_var(self.path, 'holeli', "Hole", "Holes", 0, 2)
        self.check_var_exists(self, 'gridli', "Grid", 'use_grid')
        self.check_var_exists(self, 'randomli', "Random points", 'use_random')

    def check_required_var(self, parent, var_to_check, var_str, post_str):
        """Confirm that parent has a required variable; else, raise
        ProfileError.
        """
        if not hasattr(parent, var_to_check):
            raise ProfileError(self, "%s not found in input file" % var_str)
        else:
            sys.stdout.write("  %s: %s %s\n"
                             % (var_str, parent.__dict__[var_to_check],
                                post_str))

    @staticmethod
    def check_list_len(var, min_len):
        """Return True if var is a list and has at least min_len
        elements, else False.
        """
        return isinstance(var, list) and len(var) >= min_len

    def check_list_var(self, parent, var_to_check, var_str, post_str, min_len):
        """Confirms that parent has a var_to_check that is a list and
        has at least min_len elements; if var_to_check does not exist
        and min_len <= 0, assigns an empty list to var_to_check. Else,
        raise a ProfileError.
        """
        if not hasattr(parent, var_to_check):
            if min_len > 0:
                raise ProfileError(self, "%s not found in input file"
                                   % var_str)
            else:
                parent.__dict__[var_to_check] = []
        elif not self.check_list_len(parent.__dict__[var_to_check], min_len):
            raise ProfileError(self, "%s has too few coordinates" % var_str)
        if post_str != '':
            post_str = " " + post_str
        sys.stdout.write("  %s%s: %d\n"
                         % (var_str, post_str,
                            len(parent.__dict__[var_to_check])))

    def check_table_var(self, parent, var_to_check, var_str_singular,
                        var_str_plural, min_len_1, min_len_2):
        """Confirms that var_to_check exists, is a list and has at
        least min_len_1 elements, and that each of these has at least
        min_len_2 subelements; if var_to_check does not exist and
        min_len_1 <= 0, assigns an empty list to var_to_check. Else,
        raise ProfileError.
        """
        if not hasattr(parent, var_to_check):
            if min_len_1 > 0:
                raise ProfileError(self, "%s not found in input file"
                                   % var_str_plural)
            else:
                parent.__dict__[var_to_check] = []
        elif not self.check_list_len(parent.__dict__[var_to_check], min_len_1):
            raise ProfileError(self, "Too few %s found in input file"
                               % var_str_plural.lower())
        else:
            for element in parent.__dict__[var_to_check]:
                if not self.check_list_len(element, min_len_2):
                    raise ProfileError(self, "%s has too few coordinates"
                                       % var_str_singular)
        sys.stdout.write("  %s: %d\n" % (var_str_plural,
                                         len(parent.__dict__[var_to_check])))

    @staticmethod
    def check_var_default(parent, var_to_check, var_str, default=""):
        """Checks if var_to_check exists; if not, assign the default
        value to var_to_check. Never raises a ProfileError.
        """
        if not hasattr(parent, var_to_check):
            parent.__dict__[var_to_check] = default
        sys.stdout.write("  %s: %s\n" % (var_str,
                                         parent.__dict__[var_to_check]))

    def check_var_exists(self, parent, var_to_check, var_str, optflag):
        """Checks for consistency between profiles with respect to the
        existence of var_to_check (i.e., var_to_check must be present
        either in all profiles or in none).

        If optflag is not set (i.e., this is the first profile), then
        set optflag to True or False depending on the existence of
        var_to_check. If optflag is already set (for consequent
        profiles), var_to_check must (if optflag is True) or must not
        (if optflag is False) exist. If not so, raise ProfileError.
        """
        if not hasattr(parent.opt, optflag):
            if hasattr(self, var_to_check):
                parent.opt.__dict__[optflag] = True
            else:
                parent.opt.__dict__[optflag] = False
        if parent.opt.__dict__[optflag]:
            if hasattr(parent, var_to_check):
                sys.stdout.write("  %s: yes\n" % var_str)
            else:
                raise ProfileError(self, "%s not found in input file" % var_str)
        elif hasattr(parent, var_to_check):
            raise ProfileError(self, "%s found but not expected" % var_str)
        else:
            sys.stdout.write("  %s: no\n" % var_str)

    def check_var_val(self, parent, var_to_check, var_str, optvar):
        """Checks for consistency between profiles with respect to the
        value of var_to_check (i.e., var_to_check must be present and
        have equal value in all profiles).

        If optvar is not set (i.e., this is the first profile), then
        set optflag to the value of var_to_check. If optvar is already
        set (for consequent profiles), the value of var_to_check must
        be equal to that of optvar. If not so, raise ProfileError.
        """
        if not hasattr(parent, var_to_check):
            raise ProfileError(self, "%s not found in input file" % var_str)
        if not hasattr(parent.opt, optvar):
            parent.opt.__dict__[optvar] = parent.__dict__[var_to_check]
        elif parent.__dict__[var_to_check] == parent.opt.__dict__[optvar]:
            pass  # really no point in pointing out that it's ok
            #sys.stdout.write("  %s: %s\n"
            #                 % (var_str, parent.__dict__[var_to_check]))
        else:
            raise ProfileError(self, "%s value '%s'  differs from the value "
                                     "specified ('%s') in the first input file"
                               % (var_str, parent.__dict__[var_to_check],
                                  parent.opt.__dict__[optvar]))

    def __check_paths(self):
        """Check if profile border and holes intersect with themselves."""

        def check_path(_path, s):
            for p in range(0, len(_path) - 3):
                for q in range(0, len(_path) - 1):
                    if p not in (q, q + 1) and p + 1 not in (q, q + 1):
                        if geometry.segment_intersection(_path[p],
                                                         _path[p + 1],
                                                         _path[q],
                                                         _path[q + 1]):
                            raise ProfileError(
                                self, "%s invalid (crosses itself)" % s)
            return True

        check_path(self.path, "Profile border")
        for path in self.path.holeli:
            check_path(path, "Hole")
        for n, h in enumerate(self.path.holeli):
            if not h.is_simple_polygon():
                raise ProfileError(self,
                                   "Profile hole %d is not a simple polygon"
                                   % (n + 1))
            for n2, h2 in enumerate(self.path.holeli[n + 1:]):
                if h.overlaps_polygon(h2):
                    raise ProfileError(self,
                                       "Profile hole %d overlaps with hole %d "
                                       % (n + 1, n + n2 + 2))
        sys.stdout.write("  Paths are ok.\n")

    def __get_coords(self, strli, coord_type=""):
        """Pop point coordinates from list strli.

        When an element of strli is not a valid point, a warning is
        issued.
        """
        pointli = []
        s = strli.pop(0).replace("\n", "").replace(" ", "").strip()
        while s != "END":
            try:
                p = geometry.Point(float(s.split(",")[0]),
                                   float(s.split(",")[1]))
                if pointli and (p == pointli[-1] or
                                (coord_type in ('point', 'random')
                                and p in pointli)):
                    sys.stdout.write("Duplicate %s coordinates %s: skipping "
                                     "2nd instance\n" % (coord_type, p))
                else:
                    pointli.append(p)
            except ValueError:
                if s[0] != "#":
                    profile_warning(self, "'%s' not valid %s coordinates"
                                    % (s, coord_type))
                else:
                    pass
            s = strli.pop(0).replace("\n", "").strip()
        # For some reason, sometimes the endnodes have the same coordinates;
        # in that case, delete the last endnode to avoid division by zero
        if (len(pointli) > 1) and (pointli[0] == pointli[-1]):
            del pointli[-1]
        return pointli

    def __save_results(self):
        """ Output results from a single synapse to file
        """

        def fwrite(*args):
            f.writerow(args)

        try:
            self.outputfn = os.path.join(self.opt.output_dir,
                                         self.opt.output_filename_suffix +
                                         os.path.basename(self.inputfn)
                                         + self.opt.output_filename_ext)
            if (os.path.exists(self.outputfn) and
                    self.opt.action_if_output_file_exists == 'enumerate'):
                self.outputfn = file_io.enum_filename(self.outputfn, 2)
            sys.stdout.write("Writing to '%s'...\n" % self.outputfn)
            if self.opt.output_file_format == "csv":
                csv_format = {'dialect': 'excel', 'lineterminator': '\n'}
                if self.opt.csv_delimiter == 'tab':
                    csv_format['delimiter'] = '\t'
                f = unicode_csv.Writer(file(self.outputfn, "w"),
                                       **self.opt.csv_format)
            elif self.opt.output_file_format == 'excel':
                import xls
                f = xls.Writer(self.outputfn)
            fwrite("Table 1. Profile-centric data")
            fwrite("Source image:", self.src_img)
            fwrite("Profile ID:", self.ID)
            fwrite("Comment:", self.comment)
            fwrite("Pixel width:", stringconv.tostr(float(self.pixelwidth), 2),
                   self.metric_unit)
            fwrite("Number of points (total):", len(self.pli))
            fwrite("Number of random points (total):", len(self.randomli))
            fwrite("Table 2. Point-centric data")
            columnheadings = ["Point number (as appearing in input file)",
                              "Point coordinates (in pixels)"]
            fwrite(*columnheadings)
            f.writerows([[n + 1,
                          str(p)]
                         for n, p in enumerate(self.pli)])
            fwrite("Table 3. Random point-centric data")
            columnheadings = [
                "Random point number (as appearing in input file)",
                "Random point coordinates (in pixels)"]
            fwrite(*columnheadings)
            f.writerows([[n + 1,
                          str(r)]
                         for n, r in enumerate(self.randomli)])
            f.close()
        except IOError:
            raise ProfileError(self, "Unable to write to file '%s'"
                               % self.outputfn)
        sys.stdout.write("Done.\n")
        return 1

# end of class Profile


class OptionData:
    def __init__(self):
        self.input_file_list = []
        self.spatial_resolution = 25
        self.shell_width = 0  # Skip points farther than this from profile
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
        self.stop_requested = False

    def reset(self):
        """ Resets all options to default, and removes those that are not
            set in __init__().
        """
        self.__dict__ = {}
        self.__init__()
# end of class OptionData


class ProfileError(exceptions.Exception):
    def __init__(self, profile, msg):
        self.args = (profile, msg + ".")


def profile_warning(profile, msg):
    """Issue a warning to stdout and set profile warnflag"""
    sys.stdout.write("Warning: %s.\n" % msg)
    profile.warnflag = True


def profile_message(msg):
    """Write a message to stdout"""
    sys.stdout.write("%s.\n" % msg)
