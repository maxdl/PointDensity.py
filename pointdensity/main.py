# -*- coding: utf-8 -*-

from __future__ import with_statement
import sys
import os.path
import time
import datetime
from core import *
import geometry
from file_io import *
import version
import stringconv

#
# Functions
#


def saveOutput(profileli, opt):
    """ Save a summary of results of evaluated profiles
    """
    def m(x, pixelwidth):
            return geometry.toMetricUnits(x, pixelwidth)

    def m2(x, pixelwidth):
            return geometry.toMetricUnits(x, pixelwidth**2)  # for area units...

    def na(x):
        if x in (None, -1):
            return "N/A"
        else:
            return x


    def writeSessionSummary():
        with FileWriter("session.summary", opt) as f:
            f.writerow(["%s version:" % version.title,
                       "%s (Last modified %s %s, %s)"
                       % ((version.version,) + version.date)])
            f.writerow(["Number of evaluated profiles:", len(eval_proli)])
            if err_fli:
                f.writerow(["Number of non-evaluated profiles:",
                            len(err_fli)])
            f.writerow(["Metric unit:", eval_proli[0].metric_unit])
            f.writerow(["Spatial resolution:", opt.spatial_resolution,
                        eval_proli[0].metric_unit])
            f.writerow(["Shell width:", opt.shell_width,
                        eval_proli[0].metric_unit])
            f.writerow(["Interpoint distances calculated:",
                        yes_or_no(opt.determine_interpoint_dists)])
            if opt.determine_interpoint_dists:
                f.writerow(["Interpoint distance mode:",
                            opt.interpoint_dist_mode])
                f.writerow(["Shortest interpoint distances:",
                            yes_or_no(opt.interpoint_shortest_dist)])
                f.writerow(["Lateral interpoint distances:",
                            yes_or_no(opt.interpoint_lateral_dist)])
            f.writerow(["Monte Carlo simulations performed:",
                        yes_or_no(opt.run_monte_carlo)])
            if opt.run_monte_carlo:
                f.writerow(["Number of Monte Carlo runs:",
                            opt.monte_carlo_runs])
                f.writerow(["Monte Carlo simulation window:",
                            opt.monte_carlo_simulation_window])
                f.writerow(["Strict localization in simulation window:",
                            yes_or_no(opt.monte_carlo_strict_location)])
            f.writerow(["Clusters determined:",
                        yes_or_no(opt.determine_clusters)])
            if opt.determine_clusters:
               f.writerow(["Within-cluster distance:",
                           opt.within_cluster_dist,
                           eval_proli[0].metric_unit])
            if clean_fli:
                f.writerow(["Input files processed cleanly:"])
                f.writerows([[fn] for fn in clean_fli])
            if nop_fli:
                f.writerow(["Input files processed but which generated no "
                            "point distances:"])
                f.writerows([[fn] for fn in nop_fli])
            if warn_fli:
                f.writerow(["Input files processed but which generated "
                            "warnings (see log for details):"])
                f.writerows([[fn] for fn in warn_fli])
            if err_fli:
                f.writerow(["Input files not processed or not included in "
                            "summary (see log for details):"])
                f.writerows([[fn] for fn in err_fli])


    def writeProfileSummary():
        with FileWriter("profile.summary", opt) as f:
            f.writerow(["Perimeter",
                        "Area",
                        "Number of points (total)",
                        "Number of points within profile",
                        "Number of points associated with profile",
                        "Number of points associated with border",
                        "Area density of points within profile",
                        "Profile ID",
                        "Input file",
                        "Comment"])
            f.writerows([[m(pro.path.perimeter(), pro.pixelwidth),
                          m2(pro.path.area(), pro.pixelwidth),
                          len(pro.pli),
                          len([p for p in pro.pli
                               if p.is_within_profile(pro.path)]),
                          len([p for p in pro.pli
                               if (p.is_within_profile(pro.path) or
                                   p.isAssociatedWithPath)]),
                          len([p for p in pro.pli
                                    if p.isAssociatedWithPath]),
                          1e6*(len([p for p in pro.pli
                                     if p.is_within_profile(pro.path)])
                                 / m2(pro.path.area(), pro.pixelwidth)),
                          pro.ID,
                          os.path.basename(pro.inputfn),
                          pro.comment]
                          for pro in eval_proli])

                      
    def writePointSummary(pType):
        if pType == "point":
            pli = "pli"
            pstr = "point"
        elif pType == "random":
            if not opt.use_random:
                return
            else:
                pli = "randomli"
                pstr = "point"
        elif pType == "grid":
            if not opt.use_grid:
                return
            else:
                pli = "gridli"
                pstr = "point"
        else:
            return
        with FileWriter("%s.summary" % pType, opt) as f:
            f.writerow(["%s number (as appearing in input file)"
                            % pstr.capitalize(),
                        "Distance to profile border",                                                
                        "Within profile",
                        "Profile border-associated",
                        "Profile-associated",                      
                        "Profile ID",
                        "Input file",
                        "Comment"])
            f.writerows([[n+1, 
                          m(p.distToPath, pro.pixelwidth),                                                    
                          yes_or_no(p.is_within_profile(pro.path)),
                          yes_or_no(p.isAssociatedWithPath),  
                          yes_or_no(p.is_within_profile(pro.path) or
                                    p.isAssociatedWithPath),  
                          pro.ID,
                          os.path.basename(pro.inputfn), 
                          pro.comment]
                          for pro in eval_proli for n, p in enumerate(pro.__dict__[pli])])


    def writeClusterSummary():
        if not opt.determine_clusters:
            return
        with FileWriter("cluster.summary", opt) as f:
            f.writerow(["Cluster number",
                        "Number of points in cluster",
                        "Distance to profile border of centroid",
                        "Distance to nearest cluster along border",
                        "Profile ID",
                        "Input file",
                        "Comment"])
            f.writerows([[n + 1,
                          len(c),
                          m(c.distToPath, pro.pixelwidth),
                          m(na(c.distToNearestCluster), pro.pixelwidth),
                          pro.ID,
                          os.path.basename(pro.inputfn),
                          pro.comment]
                  for pro in eval_proli for n, c in enumerate(pro.clusterli)])


    def writeInterpointSummaries():

        def _m(x):
            return m(x, pro.pixelwidth)

        if not opt.determine_interpoint_dists:
            return
        ipRels = dict([(key, val)
                        for key, val in opt.interpoint_relations.items()
                        if val and "simulated" not in key])
        if not opt.use_random:
            for key, val in opt.interpoint_relations.items():
                if "random" in key and val:
                    del ipRels[key]
        if (len(ipRels) == 0 or not
            (opt.interpoint_shortest_dist or opt.interpoint_lateral_dist)):
            return
        table = []
        if opt.interpoint_dist_mode == 'all':
            s = "all distances"
        else:
            s = "nearest neighbour distances"
        table.append(["Mode: " + s])
        headerli = ipRels.keys()
        prefixli = []
        for key, val in ipRels.items():
            prefix = key[0] + key[key.index("- ") + 2] + "_"
            #if prefix[0] == prefix[1]:
            #    prefix = prefix.replace(prefix[0], "", 1)
            prefixli.append(prefix)
        if opt.interpoint_shortest_dist and opt.interpoint_lateral_dist:
            headerli.extend(headerli)
            prefixli.extend(map(lambda s: s + "lat", prefixli))
        topheaderli = []
        if opt.interpoint_shortest_dist:
            topheaderli.append("Shortest distances")
            if opt.interpoint_lateral_dist:
                topheaderli.extend([""] * (len(ipRels)-1))
        if opt.interpoint_lateral_dist:
            topheaderli.append("Lateral distances along postsynaptic element membrane")
        table.extend([topheaderli, headerli])
        cols = [[] for c in prefixli]
        for pro in eval_proli:
            for n, li in enumerate([pro.__dict__[prefix + "distli"]
                                    for prefix in prefixli]):
                cols[n].extend(map(_m, li))
        # transpose cols and append to table
        table.extend(map(lambda *col: [e if e is not None else "" for e in col],
                         *cols))
        with FileWriter("interpoint.summary", opt) as f:
            f.writerows(table)

    def writeMonteCarloDistToBorderSummary():

        def m_li(*li):
            return [m(x, pro.pixelwidth) for x in li]

        if not opt.run_monte_carlo:
            return
        table = []
        table.append(["Run %d" % (n + 1)
                     for n in range(0, opt.monte_carlo_runs)])
        for pro in eval_proli:
            table.extend(map(m_li, *[[p.distToPath for p in li["pli"]]
                                        for li in pro.mcli]))
        with FileWriter("simulated.border.distance.summary", opt) as f:
            f.writerows(table)


    def writeMonteCarloIPDists(dist_type):

        def m_li(*li):
            return [m(x, pro.pixelwidth) for x in li]

        if not opt.run_monte_carlo:
            return
        for ip_type in [key for key, val in opt.interpoint_relations.items()
                        if "simulated" in key and val]:
            if ((dist_type == "shortest" and not opt.interpoint_shortest_dist) or
                (dist_type == "lateral" and not opt.interpoint_lateral_dist)):
                return
            if dist_type == "lateral":
               short_dist_type = "lat"
            else:
               short_dist_type = ""
            table = []
            table.append(["Run %d" % (n + 1)
                         for n in range(0, opt.monte_carlo_runs)])
            for pro in eval_proli:
                table.extend(map(m_li,
                                 *[p for li in pro.mcli
                                    for p in li[ip_type]
                                               ["%sdist" % short_dist_type]]))
            with FileWriter("%s.interpoint.%s.distance.summary"
                            % (ip_type.replace(" ", ""), dist_type), opt) as f:
                f.writerows(table)

    def writeMonteCarloClusterSummary():
        if not (opt.determine_clusters and opt.run_monte_carlo):
            return
        table = []
        table.append(["N points in cluster", "Run",
                     "Distance to postsynaptic element membrane from centroid",
                     "Distance to nearest cluster",
                     "Profile ID",
                     "Input file",
                     "Comment"])
        for pro in eval_proli:
            for n in range (0, opt.monte_carlo_runs):
                for c in pro.mcli[n]["clusterli"]:
                    table.append([len(c), n + 1,
                                 m(c.distToPath, pro.pixelwidth),
                                 m(na(c.distToNearestCluster), pro.pixelwidth),
                                 pro.ID,
                                 os.path.basename(pro.inputfn),
                                 pro.comment])
        with FileWriter("simulated.cluster.summary", opt) as f:
            f.writerows(table)


    sys.stdout.write("\nSaving summaries...\n")
    opt.save_result = {'any_saved': False, 'any_err': False}
    eval_proli = [pro for pro in profileli if not pro.errflag]
    clean_fli = [pro.inputfn for pro in profileli if not
                    (pro.errflag or pro.warnflag)]
    warn_fli = [pro.inputfn for pro in profileli if pro.warnflag]
    err_fli = [pro.inputfn for pro in profileli if pro.errflag]
    nop_fli = [pro.inputfn for pro in profileli if not pro.pli]
    if opt.output_file_format == 'excel':
        import xls
    elif opt.output_file_format == 'csv':
        csv_format = { 'dialect' : 'excel', 'lineterminator' : '\n'}
        if opt.csv_delimiter == 'tab':
            csv_format['delimiter'] = '\t'  
    writeSessionSummary()
    writeProfileSummary()
    writePointSummary("point")
    writePointSummary("random")
    writePointSummary("grid")
    writeInterpointSummaries()
    writeClusterSummary()
    writeMonteCarloDistToBorderSummary()
    writeMonteCarloIPDists("shortest")
    writeMonteCarloIPDists("lateral")
    writeMonteCarloClusterSummary()
    if opt.save_result['any_err'] == True:
        sys.stdout.write("Note: One or more summaries could not be saved.\n")
    if opt.save_result['any_saved'] == True:
        sys.stdout.write("Done.\n")
    else:
        sys.stdout.write("No summaries saved.\n")
    
def resetOptions(opt):
    """ Deletes certain options that should always be set anew for each run
        (each time the "Start" button is pressed)
    """
    if hasattr(opt, "metric_unit"):
        delattr(opt, "metric_unit")
    if hasattr(opt, "use_grid"):
        delattr(opt, "use_grid")
    if hasattr(opt, "use_random"):
        delattr(opt, "use_random")

def showOptions(opt):    
    sys.stdout.write("{} version: {} (Last modified {} {}, {})\n".format(
                      version.title, version.version, *version.date))
    sys.stdout.write("Output file format: %s\n" % opt.output_file_format)
    sys.stdout.write("Suffix of output files: %s\n"
                        % opt.output_filename_suffix)
    sys.stdout.write("Output directory: %s\n" % opt.output_dir)
    sys.stdout.write("Spatial resolution: %d\n" % opt.spatial_resolution)
    sys.stdout.write("Shell width: %d metric units\n" % opt.shell_width)
    sys.stdout.write("Interpoint distances calculated: %s\n"
                     % yes_or_no(opt.determine_interpoint_dists))
    if opt.determine_interpoint_dists:
        sys.stdout.write("Interpoint distance mode: %s\n"
                         % opt.interpoint_dist_mode.capitalize())
        sys.stdout.write("Shortest interpoint distances: %s\n"
                         % yes_or_no(opt.interpoint_shortest_dist))
        sys.stdout.write("Lateral interpoint distances: %s\n"
                         % yes_or_no(opt.interpoint_lateral_dist))
    sys.stdout.write("Monte Carlo simulations performed: %s\n"
                     % yes_or_no(opt.run_monte_carlo))
    if opt.run_monte_carlo:
        sys.stdout.write("Number of Monte Carlo runs: %d\n"
                         % opt.monte_carlo_runs)
        sys.stdout.write("Monte Carlo simulation window: %s\n"
                         % opt.monte_carlo_simulation_window)
        sys.stdout.write("Strict localization in simulation window: %s\n"
                         % yes_or_no(opt.monte_carlo_strict_location))
    sys.stdout.write("Clusters determined: %s\n" %
                     yes_or_no(opt.determine_clusters))
    if opt.determine_clusters:
       sys.stdout.write("Within-cluster distance: %d\n"
                        % opt.within_cluster_dist)

def getOutputFormat(opt):
    if opt.output_file_format == 'excel':
        try:
            import xls
        except ImportError:
            sys.stdout.write("Unable to write Excel files: resorting to csv "
                             "format.\n")
            opt.output_file_format = "csv"
    if opt.output_file_format == 'csv':
        opt.output_filename_ext = ".csv"
        opt.csv_format = { 'dialect' : 'excel', 'lineterminator' : '\n',
                       'encoding': sys.getfilesystemencoding() }
        if opt.csv_delimiter == 'tab':
            opt.csv_format['delimiter'] = '\t'
    if opt.output_filename_date_suffix:
        import datetime
        opt.output_filename_suffix = "." + datetime.date.today().isoformat()
    if opt.output_filename_other_suffix != '':
        opt.output_filename_suffix += "." + opt.output_filename_other_suffix

      
def mainProc(parent, opt):
    """ Process profile data files
    """
    
    def removeDuplicateFilenames(fli):
        """ Remove duplicate filenames in input file list
        """
        for f in fli:
            if fli.count(f) > 1:
                sys.stdout.write("Duplicate input filename %s:\n   => " 
                                 "removing first occurrence in list\n" % f)
                fli.remove(f)    
    

    if not opt.input_file_list:
        sys.stdout.write("No input files.\n")
        return 0                 
    i, n = 0, 0
    profileli = []
    sys.stdout.write("--- Session started %s local time ---\n" 
                      % time.ctime())
    removeDuplicateFilenames(opt.input_file_list)
    getOutputFormat(opt)
    resetOptions(opt)
    showOptions(opt)
    while True:
        if i < len(opt.input_file_list):
            inputfn = opt.input_file_list[i]
            i += 1
        else: 
            sys.stdout.write("\nNo more input files...\n")
            break
        parent.process_queue.put(("new_file", inputfn))
        profileli.append(ProfileData(inputfn, opt))
        profileli[-1].process(opt)
        if opt.stop_requested:
            sys.stdout.write("\n--- Session aborted by user %s local time ---\n"
                             % time.ctime())
            return 3
        if not profileli[-1].errflag:
            n += 1
            if profileli[-1].warnflag:
                sys.stdout.write("Warning(s) found while processing "
                                 "input file.\n")
                continue
        else:
            sys.stdout.write("Error(s) found while processing input file =>\n"
                             "  => No distances could be determined.\n")
            continue
    # no more input files
    errfli = [pro.inputfn for pro in profileli if pro.errflag]
    warnfli = [pro.inputfn for pro in profileli if pro.warnflag]
    if errfli:
        sys.stdout.write("\n%s input %s generated one or more "
                        "errors:\n"
                         % (stringconv.plurality("This", len(errfli)),
                            stringconv.plurality("file", len(errfli))))
        sys.stdout.write("%s\n" % "\n".join([fn for fn in errfli]))
    if warnfli:
        sys.stdout.write("\n%s input %s generated one or more warnings:\n"
                         % (stringconv.plurality("This", len(warnfli)),
                            stringconv.plurality("file", len(warnfli))))
        sys.stdout.write("%s\n" % "\n".join([fn for fn in warnfli]))
    if n > 0:
        parent.process_queue.put(("saving_summaries", ""))
        saveOutput(profileli, opt)
    else:
        sys.stdout.write("\nNo files processed.\n")
    sys.stdout.write("--- Session ended %s local time ---\n" % time.ctime())
    parent.process_queue.put(("done",""))
    opt.reset()
    if errfli: 
        return 0
    elif warnfli: 
        return 2
    else: 
        return 1
# End of main.py
