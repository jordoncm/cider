#!/bin/bash

cd `dirname $0`/..

VERSION=$1

rm -rf build
rm -rf dist

mkdir build
mkdir build/cider-$VERSION

cp -r static build/cider-$VERSION/
cp -r templates build/cider-$VERSION/
cp -r tornado build/cider-$VERSION/
cp configuration.json build/cider-$VERSION/
cp license.txt build/cider-$VERSION/
cp readme.txt build/cider-$VERSION/
cp server.py build/cider-$VERSION/
cp log.py build/cider-$VERSION/
cp collaborate.py build/cider-$VERSION/

cd build
tar -czf cider-$VERSION.tar.gz cider-$VERSION

cd ..
mkdir dist
cp build/cider-$VERSION.tar.gz dist/