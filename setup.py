#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join, dirname

PACKAGE = "pointdensity"
NAME = "PointDensity"
DESCRIPTION = "Tool for analysis of immunogold labelling"
AUTHOR = "Max Larsson"
AUTHOR_EMAIL = "max.larsson@liu.se"
LICENSE="MIT"
URL = "http://www.hu.liu.se/forskning/larsson-max/software"
VERSION = __import__(PACKAGE).__version__
REQUIRES=['pyexcelerator']

setup(
    name=NAME,
    version=__import__(PACKAGE).__version__,
    description=DESCRIPTION,
    long_description=open(join(dirname(__file__), "README.md")).read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    packages=find_packages(),
    entry_points={
    'console_scripts':
        ['PointDensity = pointdensity.PointDensity:main']
    },
    install_requires=REQUIRES
)