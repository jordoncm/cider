#!/bin/bash
# Sets up a machine capable of building Cider.
#
# NOTE: Trying to take this OS agnostic, but currently still requires Debian
# base.

cd ~

VERSION_VIRTUALENV="1.10.1"

DEPS_FOLDER='.cider_dev'

# Short of compiling our own Python version the base system must have the
# development header files available.
if [ `which apt-get` != "" ] ; then
  sudo apt-get update
  sudo apt-get -y upgrade
  sudo apt-get -y install python-dev
else
  sudo yum upgrade
  sudo yum install python-devel
fi

# Use the home folder of the current user to avoid permissions issues and not
# bog down the bootstrap process when using Vagrant by having larger file
# downloaded to the shared folder.
#
# TODO(jordoncm): Update this script to handle partial updates.
rm -rf $DEPS_FOLDER
mkdir $DEPS_FOLDER
cd $DEPS_FOLDER

# Add virtualenv to system Python. No other system level Python changes should
# be made.
wget https://pypi.python.org/packages/source/v/virtualenv/virtualenv-$VERSION_VIRTUALENV.tar.gz
tar -xzf virtualenv-$VERSION_VIRTUALENV.tar.gz
cd virtualenv-$VERSION_VIRTUALENV
sudo python setup.py install
cd ..

# Create the virtual environment.
virtualenv py
# Activate the virtualenv to make the rest of the commands easier to type.
source ~/$DEPS_FOLDER/py/bin/activate

# For SSH support.
pip install pycrypto
pip install paramiko

# PyInstaller is used to bundle the binary for distribution.
pip install pyinstaller

# pytest is the Python testing framework for Cider.
pip install pytest

# pep8 is a style checker for python code.
pip install pep8
