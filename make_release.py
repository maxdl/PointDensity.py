#! /usr/bin/env python
# -*- coding: utf-8 -*-

# A simple script to make source and Windows binary releases
# of PointDensity.py
#
#
# Usage: python create_release.py version
#
# Updates version.py to new version and date, makes a source
# distribution via 'setup.py sdist' and a Windows binary distribution
# via pyinstaller zips the binary distribution and moves both
# distributions to the ..\released directory.
#

import fileinput
import os
import sys
import datetime
from pointdensity.version import version, date


def update_version_and_date(new_ver):
    for i, line in enumerate(fileinput.input("pointdensity//version.py",
                                             inplace=1)):
        if "version" in line:
            old_ver = line.rsplit(" = ", 1)[1]
            sys.stdout.write(line.replace(old_ver, '"%s"\n' % new_ver))
        elif "date" in line:
            old_date = line.rsplit(" = ", 1)[1]
            today = datetime.date.today()
            sys.stdout.write(line.replace(old_date, '("%s", "%s", "%s")\n'
                                                    % (today.strftime("%B"),
                                                       today.strftime("%d"),
                                                       today.strftime("%Y"))))
        else:
            sys.stdout.write(line)


def yes_no_prompt(query):
    while True:
        s = raw_input(query + ' (y/n): ')
        if s.lower() == 'y':
            return True
        elif s.lower() == 'n':
            return False


try:
    new_version = sys.argv[1]
except IndexError:
    sys.stdout.write("No new version number supplied. Cancelling.\n")
    sys.exit(1)
sys.stdout.write("Preparing PointDensity.py for release...\n")
# Don't bother checking if the new version is valid or larger
# than the previous version, but ask for confirmation
if not yes_no_prompt("Update version %s (dated %s %s, %s) of PointDensity.py "
                     "to version %s?"
                     % ((version,) + date + (new_version, ))):
    sys.stdout.write("Cancelling release.\n")
    sys.exit(1)
update_version_and_date(new_version)
os.system("python setup.py sdist")
os.system("pyinstaller PointDensity.spec")
os.system("zip -j ..\\released\\PointDensity.py.-%s.x86 dist\\PointDensity\\*.*"
          % new_version)