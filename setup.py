#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 01:36:42 2020

@author: tsukiyamashou
"""

from setuptools import setup, find_packages
import os

def _requires_from_file(filename):
    print(os.getcwd())
    return open(filename).read().splitlines()

if __name__ == "__main__":
    setup(
        name='Mockup',
        version='0.0.1',
        description="this package is a mock up for CLI",
        author="zyuyou_souhatsu_group",
        install_requires=["requests","pandas","datetime"],
        #install_requires = _requires_from_file('requirements.txt'),
        #packages = setuptools.find_packages("."),
        packages = ["commands","lib"],
        entry_points={
            'console_scripts':[
                'sc = commands.main:main',
            ],
        },
        classifiers=[
        "Programming Language :: Python :: 3.7.6",
        "License :: OSI Approved :: KIT",
        "Operating System :: OS Independent",
    ]
    )
































