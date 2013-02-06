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
"""General handlers for the application."""

import hashlib
import json
import tornado.template
import tornado.web
import tornado.websocket
import os

import collaborate
import util

SFTP = False
try:
    import handlers.sftp
    SFTP = True
except ImportError:
    SFTP = False

class EditorWebSocketHandler(tornado.websocket.WebSocketHandler):
    """Web socket handlers that pipes the collaborative edting data."""
    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(
            self,
            application,
            request,
            **kwargs
        )
        self.file = None
        self.name = None
        self.salt = None

    def open(self):
        self.file = None
        self.name = None
        self.salt = None
        collaborate.FileSessionManager().register_session(self)

    def on_message(self, message):
        message_object = json.loads(message)
        if message_object['t'] == 'f':
            self.file = message_object['f']
            self.name = message_object['n']
            self.salt = message_object['s']
            sessions = collaborate.FileSessionManager().get_sessions(
                self.file,
                self.salt
            )
            names = []
            for i in sessions:
                names.append(i.name)
            collaborate.FileSessionManager().broadcast(
                self.file,
                self.salt,
                {
                    't': 'n',
                    'n': names
                }
            )
        elif message_object['t'] == 'd' and self.file is not None:
            collaborate.FileSessionManager().notify(self, message_object)
        elif message_object['t'] == 'i' and self.file is not None:
            collaborate.FileSessionManager().notify(self, message_object)

        diff_id = hashlib.sha224(str(self.salt) + str(self.file)).hexdigest()
        if message_object['t'] == 'f':
            if collaborate.FileDiffManager().has_diff(diff_id) is False:
                collaborate.FileDiffManager().create_diff(diff_id)
            else:
                self.write_message(
                    json.dumps(collaborate.FileDiffManager().get_all(diff_id))
                )
        else:
            collaborate.FileDiffManager().add(diff_id, message_object)

    def on_close(self):
        collaborate.FileSessionManager().unregister_session(self)
        sessions = collaborate.FileSessionManager().get_sessions(
            self.file,
            self.salt
        )
        names = []
        for i in sessions:
            names.append(i.name)
        collaborate.FileSessionManager().broadcast(
            self.file,
            self.salt,
            {
                't': 'n',
                'n': names
            }
        )
        if collaborate.FileSessionManager().has_sessions(
            self.file,
            self.salt
        ) is False:
            diff_id = hashlib.sha224(
                str(self.salt) + str(self.file)
            ).hexdigest()
            collaborate.FileDiffManager().remove_diff(diff_id)

class IndexHandler(tornado.web.RequestHandler):
    """The homepage."""
    def get(self):
        terminal_link = util.get_configuration_value('terminalLink')
        if terminal_link is not None:
            host = self.request.host
            host = host[:host.find(':')]
            terminal_link = terminal_link.replace('[host]', host)

        enable_dropbox = False
        if util.get_configuration_value('dropboxKey', '') != '':
            if util.get_configuration_value('dropboxSecret', '') != '':
                enable_dropbox = True

        enable_sftp = False
        if SFTP is True and util.get_configuration_value('enableSFTP', True):
            enable_sftp = True

        self.set_header('Content-Type', 'text/html')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('index.html').generate(
            title='Dashboard - Cider',
            config=json.dumps({
                'terminal_link': terminal_link,
                'enable_local_file_system': util.get_configuration_value(
                    'enableLocalFileSystem',
                    True
                ),
                'enable_dropbox': enable_dropbox,
                'enable_sftp': enable_sftp
            })
        ))

class TemplateHandler(tornado.web.RequestHandler):
    """Template strings for the frontend."""
    def get(self):
        """Build a set of template strings as Javascript."""
        templates = {}
        base = 'templates/js'
        files = os.listdir(base)
        for i in files:
            if os.path.isfile(os.path.join(base, i)):
                templates[
                    os.path.splitext(i)[0].replace('-', '_').upper()
                ] = open(os.path.join(base, i)).read()

        template_type = self.get_argument('type', '')
        if template_type and os.path.isdir(os.path.join(base, template_type)):
            files = os.listdir(os.path.join(base, template_type))
            for i in files:
                if os.path.isfile(os.path.join(base, template_type, i)):
                    templates['.'.join([
                        template_type,
                        os.path.splitext(i)[0].replace('-', '_').upper()
                    ])] = open(os.path.join(base, template_type, i)).read()

        self.set_header('Content-Type', 'text/javascript')
        loader = tornado.template.Loader('templates')
        self.write(loader.load('templates.js').generate(
            template_type = template_type,
            templates = templates
        ).replace('\n', ''))
