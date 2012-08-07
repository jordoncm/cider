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

VERSION=$1

./scripts/build.sh $VERSION

cd build
mv cider-$VERSION.tar.gz cider-$VERSION

cd cider-$VERSION
dh_make -e jordoncm@gmail.com -c GPL -f cider-$VERSION.tar.gz
cd ..
rm -f cider_$VERSION.orig.tar.gz

cp ../scripts/deb/control cider-$VERSION/debian/