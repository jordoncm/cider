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

import json

class FileSessionManager(object):
    _instance = None
    sessions = []
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FileSessionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    def registerSession(self, fs):
        self.sessions.append(fs)
    def unregisterSession(self, fs):
        self.sessions.remove(fs)
    def notify(self, source, message):
        for i in self.sessions:
            if i != source and i.file == source.file:
                i.write_message(json.dumps([message]))
    def broadcast(self, file, message):
        for i in self.sessions:
            if i.file == file:
                i.write_message(json.dumps([message]))
    def hasSessions(self, file):
        for i in self.sessions:
            if i.file == file:
                return True
        return False
    def getSessions(self, file):
        tmp = []
        for i in self.sessions:
            if i.file == file:
                tmp.append(i)
        return tmp