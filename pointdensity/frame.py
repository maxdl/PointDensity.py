import ConfigParser
import os
import os.path
import Queue
import sys
import threading
import time
import traceback
import wx
import file_io
import gui
import main
import stringconv
import version
import aboutdalog
import viewfiledialog


class wxFrame(gui.MainFrame):
    def __init__(self, parent):
        gui.MainFrame.__init__(self, parent)
        self.SetTitle(version.title)
        self.SetIcon(wx.Icon(version.icon, wx.BITMAP_TYPE_ICO))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetInputFileListCtrlColumns(self.InputFileListCtrl)
        dt = FileDropTarget(self)
        self.InputFileListCtrl.SetDropTarget(dt)
        self.opt = main.OptionData()
        self.configfn = os.path.normpath(os.path.expanduser('~/.%s.cfg'
                                         % version.title.lower()))
        self.GetInputDirFromConfig()
        self.LoadOptionsFromConfig()
        self.SetOptionsInUI()
        self.Fit()

    def OnAddFile(self, event):
        dlg = wx.FileDialog(self, "Choose a file", ".", "", "*%s"
                            % self.opt.input_filename_ext,
                            wx.MULTIPLE | wx.FD_CHANGE_DIR)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.AddFiles(dlg.GetPaths())
        finally:
            dlg.Destroy()
    
    def OnRemoveFile(self, event):
        while 1:
            i = self.InputFileListCtrl.GetNextItem(-1, 
                                                   state=wx.LIST_STATE_SELECTED)
            if i == -1:
                break
            else:
                self.InputFileListCtrl.DeleteItem(i)
                
    def OnViewFile(self, event):
        if self.InputFileListCtrl.GetSelectedItemCount() == 0:
            self.ShowWarning("No file selected.")
            return
        elif self.InputFileListCtrl.GetSelectedItemCount() > 1:
            self.ShowWarning("You can only view one file at a time.")
            return
        i = self.InputFileListCtrl.GetNextItem(-1, state=wx.LIST_STATE_SELECTED)
        try:
            fn = os.path.join(self.InputFileListCtrl.GetItem(i, 1).m_text,
                              self.InputFileListCtrl.GetItem(i, 0).m_text)   
        except IOError:
            self.ShowError("Could not open file.")
        dlg = viewfiledialog.wxViewFileDialog(self, fn)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()
            
    def OnInterpointCheckbox(self, event):
        self.InterpointModeChoice.Enable(self.InterpointCheckBox.GetValue())
        self.InterpointModeLabel.Enable(self.InterpointCheckBox.GetValue())
        self.InterpointRelationsCheckListBox.Enable(self.InterpointCheckBox.GetValue())
        self.InterpointRelationsLabel.Enable(self.InterpointCheckBox.GetValue())
        self.ShortestDistCheckBox.Enable(self.InterpointCheckBox.GetValue())
        self.LateralDistCheckBox.Enable(self.InterpointCheckBox.GetValue())


    def OnClusterCheckBox(self, event):
        self.ClusterDistSpinCtrl.Enable(self.ClusterCheckBox.GetValue())
        self.ClusterDistLabel.Enable(self.ClusterCheckBox.GetValue())
        self.ClusterDistUnitLabel.Enable(self.ClusterCheckBox.GetValue())        
    
    def OnMonteCarloCheckBox(self, event):
        self.MonteCarloRunsLabel.Enable(self.MonteCarloCheckBox.GetValue())
        self.MonteCarloRunsSpinCtrl.Enable(self.MonteCarloCheckBox.GetValue())
        self.SimulationWindowChoice.Enable(self.MonteCarloCheckBox.GetValue())
        self.SimulationWindowLabel.Enable(self.MonteCarloCheckBox.GetValue())
        self.StrictLocCheckBox.Enable(self.MonteCarloCheckBox.GetValue())
    

    def OnOtherSuffixCheckBox(self, event):
        self.OtherSuffixTextCtrl.Enable(self.OtherSuffixCheckBox.GetValue())
        
    def OnSaveLogCheckBox(self, event):
        self.LogFilePicker.Enable(self.SaveLogCheckBox.GetValue())
        self.IfLogExistsRadioBox.Enable(self.SaveLogCheckBox.GetValue())
        
    def OnSetOptionsAsDefault(self, event):
        if self.SaveOptionsToConfig():
            self.StatusBar.SetStatusText("Current options saved to '%s'."
                                          % self.configfn)


    def OnStart(self, event):
        if self.InputFileListCtrl.GetItemCount() == 0:
            self.ShowWarning("No files to process.")
            return
        self.GetOptionsFromUI()
        if not self.SetLog():
            return
            self.StatusBar.SetStatusText("Processing...")
        self.exitcode = 1
        event_type = ""
        msg = "Processing %s \n(File %d of %d)" % (
                                                   os.path.basename(self.opt.input_file_list[0]), 1,
                                                   len(self.opt.input_file_list))
        i = 0
        dlg = wx.ProgressDialog(version.title, msg,
                                len(self.opt.input_file_list) + 2,
                                parent=self,
                                style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_CAN_ABORT)
        pthread = ProcessThread(self.opt)
        pthread.start()
        while pthread.isAlive() or not pthread.process_queue.empty():
            if not pthread.process_queue.empty():
                (event_type, data) = pthread.process_queue.get()
                if event_type == "new_file":
                    i += 1
                    msg = "Processing %s \n(File %d of %d)" \
                        % (os.path.basename(data), i,
                           len(self.opt.input_file_list))
                if event_type == "saving_summaries":
                    i += 1
                    msg = "Saving summaries..."
                if event_type == "done":
                    i = len(self.opt.input_file_list) + 2
                    msg = "Done."
            self.log.update()
            if event_type == "done" and self.log.fn != "":
                self.StatusBar.SetStatusText("Logged to '" + self.log.fn + "'.")
            if not dlg.Update(i, msg)[0] and not self.opt.stop_requested:
                if self.YesNoDialog("Abort process?"):
                    pthread.stop()
                    dlg.Hide()
                else:
                    dlg.Resume()
            if dlg.GetSize().GetWidth() < dlg.GetBestSize().GetWidth():
                dlg.SetSize((dlg.GetBestSize().GetWidth() + 20,
                            dlg.GetBestSize().GetHeight()))
        if not pthread.error_queue.empty():
            exc_str = pthread.error_queue.get()
            if self.log.fn != "":
                self.StatusBar.SetStatusText("Logged to '" + self.log.fn + "'.")
            sys.stdout.write("\n*** %s session was unexpectedly aborted"
                             " at %s (local time). \n\nDetails:\n%s"
                             % (version.title, time.ctime(), exc_str))
            self.log.update()
            self.ShowError("An unexpected error occurred while executing "
                           "%s - session aborted.\n\nDetails (also "
                           "sent to log):\n\n %s" % (version.title, exc_str))
            dlg.Destroy()
            return
        # Processing finished.
        self.log.update()
        if self.log.fn != "":
            self.StatusBar.SetStatusText("Logged to '" + self.log.fn + "'.")
        dlg.Destroy()
        if pthread.exitcode == 0:
            self.ShowError("One or more errors occurred during processing. "
                           "See log for details.")
        elif pthread.exitcode == 2:
            self.ShowWarning("One or more warnings occurred during "
                             "processing. See log for details.")
        elif pthread.exitcode == 3:
            self.ShowWarning("Session aborted by user.")
            


    def OnAbout(self, event):
        dlg = aboutdalog.wxAboutDialog(self)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()


    def OnClose(self, event):
        self.SaveInputDirToConfig()
        sys.stdout = sys.__stdout__
        self.Destroy()

#
#   utilities
#

    def SaveInputDirToConfig(self):
        config = ConfigParser.ConfigParser()
        try:
            config.read(self.configfn)
        except (ConfigParser.ParsingError,
                ConfigParser.MissingSectionHeaderError):
            pass  # Silently suppress parsing errors at this stage
        if not config.has_section("Previous session"):
            config.add_section('Previous session')
        config.set('Previous session', "input_dir",
                   os.getcwdu().encode(sys.getfilesystemencoding()))
        try:
            f = open(self.configfn, 'wb')
            config.write(f)
        except IOError:
            self.ShowWarning("Configuration file\n(%s)\ncould not be saved."
                             % self.configfn)
        finally:
            f.close()

    def GetInputDirFromConfig(self):
        config = ConfigParser.ConfigParser()
        if not os.path.exists(self.configfn):
            return
        try:
            config.read(self.configfn)
        except (ConfigParser.ParsingError,
            ConfigParser.MissingSectionHeaderError):
            pass    # Silently suppress parsing errors at this stage
        try:
            inputdir = config.get('Previous session', 'input_dir', 0)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.ShowWarning("Configuration file '%s' is invalid.\n Using "
                             "current working directory." % self.configfn)
            return
        try:
            if not os.path.isdir(inputdir):
                raise IOError
            os.chdir(inputdir)
        except (IOError, TypeError):
            self.ShowWarning("Invalid input directory' %s' in configuration "
                             "file '%s'.\n Using current working directory."
                             % (inputdir, self.configfn))


    def SaveOptionsToConfig(self):

        def SetOption(option):
            config.set('Options', option, str(getattr(self.opt, option)))

        def SetDictOption(option):
            optdict = getattr(self.opt, option)
            for key, val in optdict.items():
                optstr = '.'.join([option, key.replace(' ', '_')])
                config.set('Options', optstr, str(val))

        self.GetOptionsFromUI()
        config = ConfigParser.ConfigParser()
        try:
            config.read(self.configfn)
        except (ConfigParser.ParsingError,
                ConfigParser.MissingSectionHeaderError):
            pass  # Silently suppress parsing errors at this stage
        if not config.has_section('Options'):
            config.add_section('Options')
        SetOption('output_file_format')
        SetOption('csv_delimiter')
        SetOption('action_if_output_file_exists')
        SetOption('output_filename_date_suffix')
        SetOption('spatial_resolution')
        SetOption('shell_width')
        SetOption('determine_clusters')
        SetOption('within_cluster_dist')
        SetOption('run_monte_carlo')
        SetOption('monte_carlo_runs')
        SetOption('determine_interpoint_dists')
        SetOption('monte_carlo_simulation_window')
        SetOption('monte_carlo_strict_location')
        SetOption('interpoint_dist_mode')
        SetOption('interpoint_shortest_dist')
        SetOption('interpoint_lateral_dist')
        SetDictOption('interpoint_relations')
        SetDictOption('outputs')
        try:
            f = open(self.configfn, 'wb')
            config.write(f)
        except IOError:
            self.ShowWarning("Configuration file\n(%s)\ncould not be saved."
                             % self.configfn)
        finally:
            f.close()


    def LoadOptionsFromConfig(self):

        def ShowInvalidOptionWarning(option):
            self.ShowWarning("Invalid value '%s' for option '%s' in "
                             "configuration file '%s'.\nUsing default value."
                             % (getattr(self.opt, option), option,
                                self.configfn))


        def CheckStrOption(option, valid_strings=[]):
            if getattr(self.opt, option) not in valid_strings:
                ShowInvalidOptionWarning(option)
                setattr(self.opt, option, getattr(defaults, option))

        def CheckIntOption(option, lower=None, upper=None):
            try:
                setattr(self.opt, option,
                        stringconv.str_to_int(getattr(self.opt, option),
                                              lower, upper))
            except ValueError:
                ShowInvalidOptionWarning(option)
                setattr(self.opt, option, getattr(defaults, option))

        def CheckBoolOption(option):
            try:
                setattr(self.opt, option,
                        stringconv.str_to_bool(getattr(self.opt, option)))
            except ValueError:
                ShowInvalidOptionWarning(option)
                setattr(self.opt, option, getattr(defaults, option))

        def CheckBoolDictOption(option):
            optdict = getattr(self.opt, option)
            for key, val in optdict.items():
                optstr = '.'.join([option, key.replace(" ", "_")])
                if not key in getattr(defaults, option).keys():
                    self.ShowWarning("Invalid option '%s' in configuration file"
                                     " '%s'." % (optstr, self.configfn))
                    del optdict[key]
                try:
                    optdict[key] = stringconv.str_to_bool(val)
                except ValueError:
                    self.ShowWarning("Invalid value '%s' for option '%s' in "
                                "configuration file '%s'.\nUsing default value."
                                 % (val, optstr, self.configfn))
                    optdict[key] = defaults[key]


        config = ConfigParser.ConfigParser()
        if not os.path.exists(self.configfn):
            return
        try:
            config.read(self.configfn)
        except (ConfigParser.ParsingError,
                ConfigParser.MissingSectionHeaderError):
            return     # Silently suppress parsing errors at this stage
        if not config.has_section('Options'):
            return     # No options present in config file; silently use
                       # default options
        defaults = main.OptionData()
        for option in config.options('Options'):
            if '.' in option:
                optdict, key = option.split('.', 1)
                key = key.replace("_", " ")
                try:
                    getattr(self.opt, optdict)[key] = config.get('Options',
                                                             option, 0)
                except AttributeError:
                    pass   # So, attribute is invalid, but continue silently
            else:
                setattr(self.opt, option, config.get('Options', option, 0))
        CheckStrOption('output_file_format', ('excel', 'csv'))
        CheckStrOption('csv_delimiter', ('comma', 'tab'))
        CheckStrOption('action_if_output_file_exists', ('enumerate', 'overwrite'))
        CheckBoolOption('output_filename_date_suffix')
        CheckIntOption('spatial_resolution', lower=0, upper=1000)
        CheckIntOption('shell_width', lower=0, upper=1000)
        CheckBoolOption('determine_clusters')
        CheckIntOption('within_cluster_dist', lower=1, upper=1000)
        CheckBoolOption('run_monte_carlo')
        CheckIntOption('monte_carlo_runs', lower=1, upper=999)
        CheckBoolOption('determine_interpoint_dists')
        CheckStrOption('monte_carlo_simulation_window', ('profile',
                                                         'profile + shell'))
        CheckBoolOption('monte_carlo_strict_location')
        CheckStrOption('interpoint_dist_mode', ('nearest neighbour', 'all'))
        CheckBoolOption('interpoint_shortest_dist')
        CheckBoolOption('interpoint_lateral_dist')
        CheckBoolDictOption('interpoint_relations')
        CheckBoolDictOption('outputs')




    def SetOptionsInUI(self):
        self.SpatResSpinCtrl.SetValue(self.opt.spatial_resolution)
        self.ShellWidthSpinCtrl.SetValue(self.opt.shell_width)
        self.InterpointCheckBox.SetValue(self.opt.determine_interpoint_dists)
        self.InterpointModeChoice.SetItems(['Nearest neighbour', 'All'])
        self.InterpointModeChoice.SetStringSelection(
            self.opt.interpoint_dist_mode)
        self.InterpointRelationsCheckListBox.SetItems(sorted([key.capitalize()
                                    for key in self.opt.interpoint_relations]))
        self.InterpointRelationsCheckListBox.SetCheckedStrings(
            [key.capitalize() for key in self.opt.interpoint_relations
                if self.opt.interpoint_relations[key] == True])
        self.ShortestDistCheckBox.SetValue(self.opt.interpoint_shortest_dist)
        self.LateralDistCheckBox.SetValue(self.opt.interpoint_lateral_dist)
        self.InterpointModeChoice.Enable(self.InterpointCheckBox.GetValue())
        self.InterpointModeLabel.Enable(self.InterpointCheckBox.GetValue())
        self.InterpointRelationsCheckListBox.Enable(
            self.InterpointCheckBox.GetValue())
        self.InterpointRelationsLabel.Enable(self.InterpointCheckBox.GetValue())
        self.ShortestDistCheckBox.Enable(self.InterpointCheckBox.GetValue())
        self.LateralDistCheckBox.Enable(self.InterpointCheckBox.GetValue())
        self.ClusterCheckBox.SetValue(self.opt.determine_clusters)
        self.ClusterDistSpinCtrl.SetValue(self.opt.within_cluster_dist)
        self.ClusterDistSpinCtrl.Enable(self.ClusterCheckBox.GetValue())
        self.ClusterDistLabel.Enable(self.ClusterCheckBox.GetValue())
        self.ClusterDistUnitLabel.Enable(self.ClusterCheckBox.GetValue())                
        self.MonteCarloCheckBox.SetValue(self.opt.run_monte_carlo)
        self.MonteCarloRunsSpinCtrl.SetValue(self.opt.monte_carlo_runs)
        self.SimulationWindowChoice.SetItems(['Profile', 'Profile + shell'])
        self.SimulationWindowChoice.SetStringSelection(
            self.opt.monte_carlo_simulation_window)
        self.StrictLocCheckBox.SetValue(self.opt.monte_carlo_strict_location)
        self.MonteCarloRunsLabel.Enable(self.MonteCarloCheckBox.GetValue())
        self.MonteCarloRunsSpinCtrl.Enable(self.MonteCarloCheckBox.GetValue())        
        self.SimulationWindowChoice.Enable(self.MonteCarloCheckBox.GetValue())
        self.SimulationWindowLabel.Enable(self.MonteCarloCheckBox.GetValue())
        self.StrictLocCheckBox.Enable(self.MonteCarloCheckBox.GetValue())
        self.OutputCheckListBox.SetCheckedStrings(
            [key.capitalize() for key in self.opt.outputs
                if self.opt.outputs[key] == True])
        if self.opt.output_file_format == 'excel':
            self.OutputFormatRadioBox.SetStringSelection('Excel')
        elif self.opt.csv_delimiter == 'comma':
            self.OutputFormatRadioBox.SetStringSelection('Comma-delimited text')
        else:
            self.OutputFormatRadioBox.SetSetStringSelection(
                'Tab-delimited text')
        self.IfOutputExistsRadioBox.SetStringSelection(
            self.opt.action_if_output_file_exists.capitalize())
        self.DateSuffixCheckBox.SetValue(self.opt.output_filename_date_suffix)
        self.OtherSuffixCheckBox.SetValue(
            self.opt.output_filename_other_suffix != '')
        self.OtherSuffixTextCtrl.SetValue(self.opt.output_filename_other_suffix)
        self.OtherSuffixTextCtrl.Enable(self.OtherSuffixCheckBox.GetValue())
        self.LogFilePickerCtrl.SetPath(version.title + '.log')
 
    def GetOptionsFromUI(self):
        self.opt.input_file_list = []
        for n in range(0, self.InputFileListCtrl.GetItemCount()):
            self.opt.input_file_list.append(os.path.join(
                                  self.InputFileListCtrl.GetItem(n, 1).m_text,
                                  self.InputFileListCtrl.GetItem(n, 0).m_text))
        for key in self.opt.outputs:
            if key.capitalize() in self.OutputCheckListBox.GetCheckedStrings():
                self.opt.outputs[key] = True
            else:
                self.opt.outputs[key] = False
        if self.OutputFormatRadioBox.GetStringSelection() == "Excel":
            self.opt.output_file_format = 'excel'
            self.opt.output_filename_ext = '.xls'
        elif (self.OutputFormatRadioBox.GetStringSelection() ==
            "Comma-delimited text"):
            self.opt.output_file_format = 'csv'
            self.opt.output_filename_ext = '.csv'
            self.opt.csv_delimiter = "comma"
        elif (self.OutputFormatRadioBox.GetStringSelection() ==
            "Tab-delimited text"):
            self.opt.output_file_format = 'csv'
            self.opt.output_filename_ext = '.csv'
            self.opt.csv_delimiter = "tab"
        self.opt.action_if_output_file_exists = \
            self.IfOutputExistsRadioBox.GetStringSelection().lower()
        self.opt.output_filename_date_suffix = self.DateSuffixCheckBox.GetValue()
        if self.OtherSuffixCheckBox.GetValue():
            self.opt.output_filename_other_suffix = \
                self.OtherSuffixTextCtrl.GetValue()
        self.opt.spatial_resolution = int(self.SpatResSpinCtrl.GetValue())
        self.opt.shell_width = int(self.ShellWidthSpinCtrl.GetValue())
        self.opt.determine_interpoint_dists = self.InterpointCheckBox.GetValue()
        for key in self.opt.interpoint_relations:
            if (key.capitalize() in
                    self.InterpointRelationsCheckListBox.GetCheckedStrings()):
                self.opt.interpoint_relations[key] = True
            else:
                self.opt.interpoint_relations[key] = False
        if not True in self.opt.interpoint_relations.values():
            self.opt.determine_interpoint_dists = False
        self.opt.interpoint_dist_mode = \
            self.InterpointModeChoice.GetStringSelection().lower()
        self.opt.interpoint_shortest_dist = self.ShortestDistCheckBox.GetValue()
        self.opt.interpoint_lateral_dist = self.LateralDistCheckBox.GetValue()
        self.opt.run_monte_carlo = self.MonteCarloCheckBox.GetValue()
        self.opt.monte_carlo_runs = self.MonteCarloRunsSpinCtrl.GetValue()
        self.opt.monte_carlo_simulation_window = \
            self.SimulationWindowChoice.GetStringSelection().lower()
        self.opt.monte_carlo_strict_location = self.StrictLocCheckBox.GetValue()
        self.opt.determine_clusters = self.ClusterCheckBox.GetValue()
        self.opt.within_cluster_dist = self.ClusterDistSpinCtrl.GetValue()
        self.GetOutputDir()

    def GetInputDir(self):
        for f in self.opt.input_file_list:
            if os.path.dirname(f):
                return os.path.dirname(f)
        return ""

    def GetOutputDir(self):
        """ """
        self.opt.output_dir = os.path.join(self.GetInputDir() or os.getcwdu(),
            "out")
        if not os.path.isdir(self.opt.output_dir):
            os.mkdir(self.opt.output_dir)

    def AddFiles(self, fli):
        if len(fli) == 0:
            return
        c  = self.InputFileListCtrl.GetItemCount()
        n = 0
        for fn in fli:
            if (os.path.isfile(fn) and
                os.path.splitext(fn)[1] == self.opt.input_filename_ext):
                self.InputFileListCtrl.InsertStringItem(c + n, os.path.basename(fn))
                self.InputFileListCtrl.SetStringItem(c + n, 1, os.path.dirname(fn))
                n += 1
            elif os.path.isdir(fn):
                for fn2 in os.listdir(fn):
                    if (os.path.isfile(os.path.join(fn, fn2)) and
                        os.path.splitext(fn2)[1] == self.opt.input_filename_ext):
                        self.InputFileListCtrl.InsertStringItem(c + n, fn2)
                        self.InputFileListCtrl.SetStringItem(c + n, 1, fn)
                        n += 1
        if n > 0:
            self.InputFileListCtrl.SetColumnWidth(0, -1)
            self.InputFileListCtrl.SetColumnWidth(1, -1)
        elif os.path.isdir(fn):
            self.ShowWarning("No files with '%s' extension found in folder(s)."
                % self.opt.input_filename_ext)
        else:
            self.ShowWarning("Input files must have a '%s' extension."
                % self.opt.input_filename_ext)


    def SetInputFileListCtrlColumns(self, parent):
        parent.InsertColumn(col = 0, format = wx.LIST_FORMAT_LEFT, 
                            heading = 'Name', width = -1)
        parent.InsertColumn(col = 1, format = wx.LIST_FORMAT_LEFT, 
                            heading = 'Path', width = -1)

    def SetLog(self):  # hm can't I simplify this?
        if self.SaveLogCheckBox.GetValue():
            mode = self.IfLogExistsRadioBox.GetStringSelection()
            logfn = self.LogFilePickerCtrl.GetPath()
            if os.path.dirname(logfn) == "":
                logfn = os.path.join(self.opt.output_dir, logfn)
            try:
                if os.path.exists(logfn):
                    if self.IfLogExistsRadioBox.GetStringSelection() == "Enumerate":
                        logfn = file_io.enumFilename(logfn, 2)
                    else:
                        f = open(logfn, "a", 0)
                        f.close()
                else:   # ok, so file doesn't exist but check if name is valid
                    f = open(logfn, "w", 0)
                    f.close()
            except IOError:
                self.ShowError("Could not write to log file. Please choose "
                               "another filename.")
                return 0
            self.log = LogQueue(self, logfn, self.LogTextCtrl, mode)
        else:
            self.log = LogQueue(self, "", self.LogTextCtrl, "")
        sys.stdout = self.log
        return 1


    def ShowWarning(self, s):
        dlg = wx.MessageDialog(self, s, version.title, 
                               wx.OK | wx.ICON_EXCLAMATION)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

    def ShowError(self, s):
        dlg = wx.MessageDialog(self, s, version.title, wx.OK | wx.ICON_HAND)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()
    
    def YesNoDialog(self, s):
        dlg = wx.MessageDialog(self, s, version.title,
            wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT)
        try:
            pressed = dlg.ShowModal()
        finally:
            dlg.Destroy()
        if pressed == wx.ID_YES:
            return True
        return False


class ProcessThread(threading.Thread):
    def __init__(self, opt):
        threading.Thread.__init__(self)
        self.opt = opt
        self.process_queue = Queue.Queue()
        self.error_queue = Queue.Queue(1)
        self.opt.stop_requested = False

    def stop(self):
        self.opt.stop_requested = True

    def run(self):
        try:
            self.exitcode = main.mainProc(self, self.opt)
        except:
            exc_str = "".join(traceback.format_exception(sys.exc_type,
                                                         sys.exc_value,
                                                         sys.exc_traceback))
            self.error_queue.put(exc_str)


class LogQueue:
    def __init__(self, parent, fn, win, mode):
        self.parent = parent
        self.fn = fn
        self.win = win
        self.encoding = sys.getfilesystemencoding()
        self.q = Queue.Queue()
        if self.fn != "":
            self.errstr = "* Error: could not write to log file: %s\n" % self.fn
        if mode == 'Append':
            try:
                f = open(self.fn, "a", 0)
                f.close()
            except IOError:
                try:
                    f = open(self.fn, "w", 0)
                    f.close()
                except IOError:
                    sys.stderr.write(self.errstr)
                    self.fn = ""
        elif mode == 'Overwrite' or mode == 'Enumerate':
            try:
                f = open(self.fn, "w", 0)
                f.close()
            except IOError:
                sys.stderr.write(self.errstr.encode(self.encoding))
                self.fn = ""

    def write(self, s):
        self.q.put(s)

    def update(self):
        while not self.q.empty():
            s = self.q.get()
            self.win.write(s)
            self.parent.Update()
            if self.fn != "":
                try:
                    f = open(self.fn, "a", 0)
                    try:
                        f.write(s.encode(self.encoding))
                    finally:
                        f.close()
                except IOError:
                    sys.stderr.write(self.errstr.encode(self.encoding))

class FileDropTarget(wx.FileDropTarget):

    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent

    def OnDropFiles(self, x, y, fli):
        self.parent.AddFiles(fli)

    
