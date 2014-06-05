# Because the csv module in Python 2.x does not support unicode, use this
# instead. Taken essentially verbatim from the python docs - see
# http://docs.python.org/library/csv.html.


import csv
import codecs
import cStringIO


class Writer(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):

        def convstr(val):
            if isinstance(val, (int, float)):
                return str(val)
            else:
                return val

        row = [convstr(e) for e in row]
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    def close(self):
        """ Not really needed; only present to make the interface similar to the
            xls.py module (xls.writer objects need to be explicitly closed)
        """
        pass
