#!/bin/bash
#
# This work is copyright 2011 - 2013 Jordon Mears. All rights reserved.
#
# This file is part of Cider.
#
# Cider is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Cider is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Cider. If not, see <http://www.gnu.org/licenses/>.

cd `dirname $0`/..
grep --color=always \
    --exclude=json2 --exclude=min --exclude=.pyc --exclude=pysftp \
    --exclude-dir=ace --exclude-dir=bootstrap --exclude-dir=tornado \
    --exclude-dir=build --exclude-dir=dist --exclude-dir=.git \
    -rni $1 .