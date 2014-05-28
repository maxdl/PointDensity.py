#
#    A simple csv module look-a-like Excel sheet writer:
#
#    Uses the pyExcelerator module to write to Excel sheets,
#    in a manner similar to the csv module
#
#    N.B. The writer object needs to be explicitly closed.
#
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


from pyExcelerator import *

class writer(object):
    def __init__(self, filename, sheetname="Sheet 1"):
        self.wb = Workbook()
        self.sheet = self.wb.add_sheet(sheetname)
        self.filename = filename
        self.curr_row = 0
                

    def writerow(self, row):
        for col, element in enumerate(row):
            if element != None:
                self.sheet.write(self.curr_row, col, element)
            else:
                self.sheet.write(self.curr_row, col, "None")
        self.curr_row += 1
            

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
    
    def close(self):
        self.wb.save(self.filename)
        