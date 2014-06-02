#
#    A simple csv module look-a-like Excel sheet writer:
#
#    Uses the pyExcelerator module to write to Excel sheets,
#    in a manner similar to the csv module
#
#    N.B. The writer object needs to be explicitly closed.


from pyExcelerator import *


class Writer(object):
    def __init__(self, filename, sheetname="Sheet 1"):
        self.wb = Workbook()
        self.sheet = self.wb.add_sheet(sheetname)
        self.filename = filename
        self.curr_row = 0

    def writerow(self, row):
        for col, element in enumerate(row):
            if element is not None:
                self.sheet.write(self.curr_row, col, element)
            else:
                self.sheet.write(self.curr_row, col, "None")
        self.curr_row += 1

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    def close(self):
        self.wb.save(self.filename)