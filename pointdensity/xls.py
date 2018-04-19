#
#    A simple csv module look-a-like Excel sheet writer:
#
#    Uses the openpyxl module to write to Excel sheets,
#    in a manner similar to the csv module
#
#    N.B. The writer object needs to be explicitly closed.

from openpyxl import Workbook


class Writer(object):
    def __init__(self, filename, sheetname="Sheet1"):
        self.wb = Workbook()
        self.sheet = self.wb.active
        self.sheet.title = sheetname
        self.filename = filename
        self.curr_row = 1

    def writerow(self, row):
        for col, element in enumerate(row):
            c = self.sheet.cell(row=self.curr_row, column=col+1)
            if isinstance(element, int):
                c.value = element
            elif isinstance(element, float):
                c.value = float(element)
            else:
                c.value = str(element) if element is not None else "None"
        self.curr_row += 1

    def writerows(self, rows):
        for r in rows:
            self.writerow(r)

    def close(self):
        self.wb.save(self.filename)