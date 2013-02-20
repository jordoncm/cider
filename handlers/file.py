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
"""Handlers to manage local filesystem requests."""

import os
import tornado.web

import handlers.mixins
import log
import util

class CreateFolderHandler(
    tornado.web.RequestHandler,
    handlers.mixins.CreateFolder
):
    """Handles the request to create a new folder."""
    def get(self):
        """GET request; takes an argument path as the full path to the folder
        to be created.
        """
        try:
            path = self.get_path()
            os.mkdir(os.path.join(
                os.path.dirname(__file__),
                util.get_base_path_adjustment(),
                path
            ))
            self.do_success()
        except:  # pylint: disable=W0702
            self.do_failure()

class DownloadHandler(tornado.web.RequestHandler, handlers.mixins.Download):
    """Handles file download requests."""
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        download.
        """
        filename = self.get_file()
        basename = util.find_base(filename)

        try:
            full_path = os.path.join(
                os.path.dirname(__file__),
                util.get_base_path_adjustment(),
                filename
            )
            file_handler = open(full_path, 'rb')
            data = file_handler.read()
            file_handler.close()
            length = os.path.getsize(full_path)
        except Exception as error:  # pylint: disable=W0703
            log.error(error)
            data = None
            length = 0

        self.do_headers(basename, length)
        self.finish(data)

class EditorHandler(tornado.web.RequestHandler, handlers.mixins.Editor):
    """Handles editor requests."""
    def get(self):
        """GET request; takes an argument file as the full path of the file to
        load into the editor.
        """
        filename = self.get_file()
        full_filename = os.path.join(
            os.path.dirname(__file__),
            util.get_base_path_adjustment(),
            filename
        )
        text = ''
        saved = False
        read_only = util.get_configuration_value('readOnly', False)
        if not read_only and os.path.exists(full_filename):
            read_only = not os.access(full_filename, os.W_OK)

        try:
            file_handler = open(full_filename, 'r')
            text = file_handler.read()
            file_handler.close()
            saved = True
        except Exception as error:  # pylint: disable=W0703
            log.warn(error)

        self.do_output(text, saved = saved, read_only = read_only)

class FileManagerHandler(
    tornado.web.RequestHandler,
    handlers.mixins.FileManager
):
    """Handles the file manager requests."""
    def get(self):
        """GET request; takes path as an argument."""
        path = self.get_path()
        base = util.get_base_path_adjustment()

        files = []
        try:
            file_list = os.listdir(os.path.join(base, path))
            for i in file_list:
                try:
                    filename = os.path.join(base, path, i)
                    is_file = os.path.isfile(filename)
                    confirm = ''
                    if is_file and os.path.getsize(filename) > 10485760:
                        confirm = 'large'
                    if is_file and not util.is_text_file(filename):
                        confirm = 'binary'
                    files.append({
                        'name': i,
                        'is_file': is_file,
                        'confirm': confirm
                    })
                except IOError as error:
                    log.warn(error)
        except Exception as error:  # pylint: disable=W0703
            log.warn(error)

        self.do_output(files, base)

class SaveFileHandler(tornado.web.RequestHandler, handlers.mixins.SaveFile):
    """Handles file saving requests."""
    def get(self):
        """GET request; takes arguments file and text for the path of the file
        to save and the content to put in it.
        """
        try:
            filename = self.get_file()
            full_filename = os.path.join(
                os.path.dirname(__file__),
                util.get_base_path_adjustment(),
                filename
            )
            read_only = util.get_configuration_value('readOnly', False)
            if not read_only and os.access(full_filename, os.W_OK):
                text = self.get_text()
                file_handler = open(full_filename, 'w')
                file_handler.write(text)
                file_handler.close()

                self.broadcast_save(filename)
                self.do_success()
            else:
                self.do_failure()
        except Exception as error:  # pylint: disable=W0703
            log.error(error)
            self.do_failure()

    def post(self):
        """Post request; same logic as the GET request."""
        self.get()
