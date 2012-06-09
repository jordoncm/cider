#!/usr/bin/env python

# 
# This work is copyright 2012 Jordon Mears. All rights reserved.
# 
# This file is part of Cider.
# 
# Cider is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cider is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cider.  If not, see <http://www.gnu.org/licenses/>.
# 

import os
import sys

if sys.platform == 'win32':
    from distutils.core import setup
    import py2exe
elif sys.platform == 'darwin':
    from setuptools import setup

def buildDataFilesPaths(source, target, paths):
    dataFiles = []
    
    filesOnLevel = []
    for path in paths:
        if os.path.isfile(os.path.join(source, path)):
            filesOnLevel.append(os.path.join(target, path))
        elif os.path.isdir(os.path.join(source, path)):
            print os.path.join(source, path)
            dataFiles.extend(buildDataFilesPaths(
                os.path.join(source, path),
                os.path.join(target, path),
                os.listdir(os.path.join(source, path))
            ))
    
    if len(filesOnLevel):
        dataFiles.append((source, filesOnLevel))
    
    return dataFiles

APP = ['server.py']
DATA_FILES = buildDataFilesPaths('', '', [
    'patch',
    'static',
    'templates',
    'configuration.json',
    'license.txt',
    'readme.txt'
])
OPTIONS = {
    'py2app' : {
        'plist' : {
        }
    },
    'py2exe' : {
        'excludes' : ['Tkinter']
    }
}

if sys.platform == 'darwin':
    setup(
        name = 'Cider',
        version = '0.4',
        author = 'Jordon Mears',
        description = ('Web-based IDE'),
        app = APP,
        data_files = DATA_FILES,
        options = OPTIONS,
        setup_requires = ['py2app']
    )
elif sys.platform == 'win32':
    setup(
        name = 'Cider',
        version = '0.4',
        author = 'Jordon Mears',
        description = ('Web-based IDE'),
        console = APP,
        data_files = DATA_FILES,
        options = OPTIONS
    )