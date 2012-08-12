#!/bin/bash

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

cd `dirname $0`/..

find . -name "*.pyc" -exec rm '{}' ';'

VERSION=$1

rm -rf build
rm -rf dist

mkdir build
mkdir build/cider-$VERSION

cp -r handlers build/cider-$VERSION/
cp -r static build/cider-$VERSION/
cp -r templates build/cider-$VERSION/
cp -r tornado build/cider-$VERSION/
cp cider build/cider-$VERSION/
cp collaborate.py build/cider-$VERSION/
cp configuration.json build/cider-$VERSION/
cp license.txt build/cider-$VERSION/
cp log.py build/cider-$VERSION/
cp readme.md build/cider-$VERSION/
cp server.py build/cider-$VERSION/
cp util.py build/cider-$VERSION/

cd build
tar -czf cider-$VERSION.tar.gz cider-$VERSION

cd ..
mkdir dist
cp build/cider-$VERSION.tar.gz dist/