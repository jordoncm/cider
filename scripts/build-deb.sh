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
dh_make --s -e jordoncm@gmail.com -c GPL -f cider-$VERSION.tar.gz
cd ..
rm -f cider_$VERSION.orig.tar.gz

mkdir cider-$VERSION/extra
cp -a ../scripts/deb/cider cider-$VERSION/extra/
cd cider-$VERSION/extra
ln -s /usr/share/cider/configuration.json cider.json
cd ../..

cp ../scripts/deb/control cider-$VERSION/debian/
cp ../scripts/deb/cider.install cider-$VERSION/debian/
cd cider-$VERSION/debian/
rm -f *ex
rm -f *EX
rm -f README*
rm -rf source
cd ..
dpkg-buildpackage -b
cd ..

mv cider_$VERSION-1_all.deb ../dist/