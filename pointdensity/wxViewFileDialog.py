#
#    Module      : wxViewFileDialog.py
#    Description : Provides dialog for viewing input files
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

import os.path
import wx
import gui

class wxViewFileDialog(gui.ViewFileDialog):
    def __init__(self, parent, fn):
        gui.ViewFileDialog.__init__(self, parent)
        try:
            self.SetTitle(os.path.basename(fn))
            f = open(fn, "r", 0)
            try:
                for s in f.readlines():
                    self.ViewFileTextCtrl.AppendText(s)
            finally:
                f.close()
        except IOError:
            parent.ShowError("Could not open file.")
            self.Close()
            
    def OnClose(self, event):
        self.Destroy()
    
    
