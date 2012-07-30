#!/bin/bash

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