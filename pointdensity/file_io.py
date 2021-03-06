import os.path
import sys


class FileWriter:
    def __init__(self, main_name, opt):
        self.main_name = main_name
        self.opt = opt
        self.format = opt.output_file_format
        self.fn = ""
        self.f = None

    def __enter__(self):
        self.fn = os.path.join(self.opt.output_dir,
                               self.main_name +
                               self.opt.output_filename_suffix +
                               self.opt.output_filename_ext)
        if (os.path.exists(self.fn) and
                self.opt.action_if_output_file_exists == 'enumerate'):
                self.fn = enum_filename(self.fn, 2)
        if self.format == 'csv':
            import csv
            self.f = csv.writer(open(self.fn, 'w'), **self.opt.csv_format)
        elif self.format == 'excel':
            from . import xls
            self.f = xls.Writer(self.fn)
        return self.f

    def __exit__(self, _type, _val, tb):
        try:
            if tb is not None:
                raise IOError
            if self.format == 'excel':
                self.f.close()
            sys.stdout.write("Saved '%s'.\n" % self.fn)
            self.opt.save_result['any_saved'] = True
        except IOError:
            sys.stdout.write("Error: Unable to save to file '%s'\n" % self.fn)
            self.opt.save_result['any_err'] = True


def enum_filename(fn, n):
    """Return a unique numbered filename based on fn"""
    fnbase, fnext = os.path.splitext(fn)
    newfn = ''.join([fnbase, "." + str(n), fnext])
    if os.path.exists(newfn):
        return enum_filename(fn, n + 1)
    else:
        return newfn


def read_file(fname):
    """Open file named fname and read its lines into a list"""
    try:
        f = open(fname, mode="r", errors="surrogateescape")
        try:
            s = f.readlines()
        finally:
            f.close()
    except (IOError, UnicodeDecodeError):
        sys.stdout.write("Error: File not found or unreadable\n")
        return False
    return s
