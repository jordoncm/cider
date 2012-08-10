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

import log


class FileSessionManager(object):
    
    _instance = None
    sessions = []
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FileSessionManager, cls).__new__(
                cls,
                *args,
                **kwargs
            )
        return cls._instance
    
    def register_session(self, fs):
        self.sessions.append(fs)
    
    def unregister_session(self, fs):
        self.sessions.remove(fs)
    
    def notify(self, source, message):
        for i in self.sessions:
            if i != source and (i.file == source.file and i.salt == source.salt):
                i.write_message(json.dumps([message]))
    
    def broadcast(self, file, salt, message):
        for i in self.sessions:
            if i.file == file and i.salt == salt:
                i.write_message(json.dumps([message]))
    
    def has_sessions(self, file, salt):
        for i in self.sessions:
            if i.file == file and i.salt == salt:
                return True
        return False
    
    def get_sessions(self, file, salt):
        tmp = []
        for i in self.sessions:
            if i.file == file and i.salt == salt:
                tmp.append(i)
        return tmp


class FileDiffManager(object):
    
    _instance = None
    diffs = {}
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FileDiffManager, cls).__new__(
                cls,
                *args,
                **kwargs
            )
        return cls._instance
    
    def create_diff(self, id):
        if self.has_diff(id) is False:
            self.diffs[id] = []
    
    def has_diff(self, id):
        return id in self.diffs
    
    def remove_diff(self, id):
        if self.has_diff(id) is True:
            del self.diffs[id]
    
    def get_all(self, id):
        if self.has_diff(id) is True:
            return self.diffs[id]
        else:
            return []
    
    def add(self, id, diff):
        if self.has_diff(id) is False:
            self.create_diff(id)
        self.diffs[id].append(diff)