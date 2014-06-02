# -*- coding: utf-8 -*-

import codecs
import os.path
import sys


class FileWriter():
    def __init__(self, main_name, opt):
        self.main_name = main_name
        self.opt = opt
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
        if self.opt.output_file_format == 'csv':
            import unicode_csv as writer
            self.f = writer.Writer(file(self.fn, 'w'),
                                        **self.opt.csv_format)
        elif self.opt.output_file_format == 'excel':
            import xls as writer
            self.f = writer.Writer(self.fn)
        return self.f

    def __exit__(self, type, val, tb):
        try:
            if tb is not None:
                raise IOError
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
        f = codecs.open(fname, mode="r", encoding="utf-8", buffering=0)
        try:
            s = f.readlines()
        finally:
            f.close()
    except IOError:
        sys.stdout.write("Error: File not found or unreadable")
        return 0
    return s
