#!/usr/bin/env python
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
"""Cider: collaborative web-based IDE.

Provides a web based file manager and collaborative IDE like code editor. See
the readme for more details.
"""

import os
import platform
import sys
import thread
import time
import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket
import webbrowser

import handlers
import handlers.auth.dropbox
import handlers.dropbox
import handlers.file
import log
import options
import util

GUI = False
try:
    from Tkinter import Tk
    from Tkinter import Menu
    GUI = True
except ImportError:
    GUI = False

SFTP = False
try:
    import handlers.sftp
    SFTP = True
except ImportError:
    SFTP = False
    log.warn(' '.join(
        'SFTP support not available.',
        'Check dependent libraries pysftp, paramiko and pycrypto.'
    ))

try:
    __file__
except NameError:
    # pylint: disable=E1101
    if hasattr(sys, 'frozen') and sys.frozen in ('windows_exe', 'console_exe'):
        __file__ = os.path.dirname(os.path.abspath(sys.executable))
    # pylint: enable=E1101

SETTINGS = {
    'autoescape': None,
    'cookie_secret': util.get_configuration_value(
        'cookieSecret',
        'aW5zZWN1cmVTZWNyZXQ='
    ),
    'dropbox_consumer_key': util.get_configuration_value('dropboxKey', ''),
    'dropbox_consumer_secret': util.get_configuration_value(
        'dropboxSecret',
        ''
    ),
    'login_url': '/',
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
}

URLS = [
    (r'/', handlers.IndexHandler),
    (r'/ws/?', handlers.EditorWebSocketHandler),
    (r'/templates.js', handlers.TemplateHandler)
]

if util.get_configuration_value('dropboxKey', '') != '':
    if util.get_configuration_value('dropboxSecret', '') != '':
        URLS = URLS + [
            (r'/auth/dropbox/?', handlers.auth.dropbox.DropboxHandler),
            (r'/dropbox/create-folder/?', handlers.dropbox.CreateFolderHandler),
            (r'/dropbox/download/?', handlers.dropbox.DownloadHandler),
            (r'/dropbox/editor/?', handlers.dropbox.EditorHandler),
            (r'/dropbox/file-manager/?', handlers.dropbox.FileManagerHandler),
            (r'/dropbox/save-file/?', handlers.dropbox.SaveFileHandler)
        ]

if util.get_configuration_value('enableLocalFileSystem', True):
    URLS = URLS + [
        (r'/file/create-folder/?', handlers.file.CreateFolderHandler),
        (r'/file/download/?', handlers.file.DownloadHandler),
        (r'/file/editor/?', handlers.file.EditorHandler),
        (r'/file/file-manager/?', handlers.file.FileManagerHandler),
        (r'/file/save-file/?', handlers.file.SaveFileHandler)
    ]

if SFTP is True and util.get_configuration_value('enableSFTP', True):
    URLS = URLS + [
        (r'/sftp/create-folder/?', handlers.sftp.CreateFolderHandler),
        (r'/sftp/download/?', handlers.sftp.DownloadHandler),
        (r'/sftp/editor/?', handlers.sftp.EditorHandler),
        (r'/sftp/file-manager/?', handlers.sftp.FileManagerHandler),
        (r'/sftp/save-file/?', handlers.sftp.SaveFileHandler)
    ]

def start():
    """Starts up the application server."""
    log.msg('Starting server...')
    # pylint: disable=W0142
    application = tornado.web.Application(URLS, **SETTINGS)
    # pylint: enable=W0142
    port = options.get('port', util.get_configuration_value('port', 3333))
    log.msg('Listening on port ' + str(port) + '.')
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

def main():
    """The main application execution."""
    try:
        thread.start_new_thread(start, ())
        suppress = options.get(
            'suppress',
            util.get_configuration_value('suppressBrowser', False)
        )
        if suppress is False:
            webbrowser.open_new_tab('http://localhost:' + str(
                options.get('port', util.get_configuration_value('port', 3333))
            ))

        if GUI and platform.system() != 'Linux':
            try:
                root = Tk()
                root.withdraw()
                menu = Menu(root)
                root.config(menu=menu)
                root.mainloop()
            except KeyboardInterrupt:
                sys.exit()
            except Exception:
                while(True):
                    time.sleep(10)
        else:
            while(True):
                time.sleep(10)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    main()
