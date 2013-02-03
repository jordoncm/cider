# This work is copyright 2012 - 2013 Jordon Mears. All rights reserved.
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
"""Handles the collaborative editing sessions and diffs."""

import json

class FileSessionManager(object):
    """Manages open sessions for a file."""
    _instance = None
    sessions = []

    def __new__(cls, *args, **kwargs):
        """Overrides in order to make this class a singleton."""
        if not cls._instance:
            cls._instance = super(FileSessionManager, cls).__new__(
                cls,
                *args,
                **kwargs
            )
        return cls._instance

    def register_session(self, file_session):
        """Appends a web socket handler to the list of sessions."""
        self.sessions.append(file_session)

    def unregister_session(self, file_session):
        """Removes a session from the list of sessions."""
        self.sessions.remove(file_session)

    def notify(self, source, message):
        """Notify all sessions editing the same file (except the source)."""
        for i in self.sessions:
            if i != source and i.file == source.file and i.salt == source.salt:
                i.write_message(json.dumps([message]))

    def broadcast(self, filename, salt, message):
        """Notify all sessions editing the same file."""
        for i in self.sessions:
            if i.file == filename and i.salt == salt:
                i.write_message(json.dumps([message]))

    def has_sessions(self, filename, salt):
        """Returns whether or not the given file has any sessions."""
        for i in self.sessions:
            if i.file == filename and i.salt == salt:
                return True
        return False

    def get_sessions(self, filename, salt):
        """Fetch the active sessions for a file."""
        tmp = []
        for i in self.sessions:
            if i.file == filename and i.salt == salt:
                tmp.append(i)
        return tmp

class FileDiffManager(object):
    """Maintains diffs for a file.

    Used to keep track of diffs in the case that a second user opens a file
    before the first user has saved it.
    """
    _instance = None
    diffs = {}

    def __new__(cls, *args, **kwargs):
        """Overrides in order to make this class a singleton."""
        if not cls._instance:
            cls._instance = super(FileDiffManager, cls).__new__(
                cls,
                *args,
                **kwargs
            )
        return cls._instance

    def create_diff(self, diff_id):
        """Creates a diff entry in the diff hash for a file."""
        if self.has_diff(diff_id) is False:
            self.diffs[diff_id] = []

    def has_diff(self, diff_id):
        """Returns whether or not target file has a diff list."""
        return diff_id in self.diffs

    def remove_diff(self, diff_id):
        """Removes a diff list from the hash (everyone has closed the file)."""
        if self.has_diff(diff_id) is True:
            del self.diffs[diff_id]

    def get_all(self, diff_id):
        """Fetches all diffs in a diff list."""
        if self.has_diff(diff_id) is True:
            return self.diffs[diff_id]
        else:
            return []

    def add(self, diff_id, diff):
        """Adds a diff to the diff list by its id."""
        if self.has_diff(diff_id) is False:
            self.create_diff(diff_id)
        self.diffs[diff_id].append(diff)
