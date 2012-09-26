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

import os
import re
import StringIO
import tornado.web

import log

class ScriptHandler(tornado.web.RequestHandler):
    """Simple on the fly Javascript code packager."""
    
    def get(self):
        self.set_header('Content-Type', 'application/javascript')
        self.write(get_deps())
        base = os.path.join('js', os.path.basename(self.request.path))
        if os.path.isfile(base + '.include'):
            includes = open(base + '.include')
            for include in includes:
                self.write(get_code(include))
            includes.close()
        if os.path.isfile(base):
            self.write(remove_whitespace(remove_comments(open(base).read())) + '\n')


def get_deps():
    return open(
        'js/deps/json2.js'
    ).read() + open(
        'js/deps/jquery.min.js'
    ).read() + open(
        'js/deps/underscore-min.js'
    ).read()


def get_code(include):
    include = include.strip()
    include_base = os.path.basename(include)
    ext = include[(include.rfind('.') + 1):]
    if include:
        if include_base == '*':
            code = StringIO.StringIO()
            folder = os.path.dirname(include)
            if os.path.isdir(os.path.join('js', folder)):
                files = os.listdir(os.path.join('js', folder))
                for file in files:
                    if os.path.isfile(os.path.join('js', folder, file)):
                        code.write(get_code(os.path.join(folder, file)))
            return code.getvalue()
        elif ext == 'html':
            try:
                loader = tornado.template.Loader('templates')
                return remove_comments(loader.load('View.js').generate(
                    namespace=os.path.dirname(include).replace('/', '.'),
                    cls=include_base[:include_base.rfind('.')],
                    template_code=remove_whitespace(open(os.path.join('js', include)).read()).replace('\'', '\\\'')
                )).replace('\n', '') + '\n'
            except IOError:
                return ''
        else:
            try:
                return remove_comments(remove_whitespace(open(os.path.join('js', include)).read())) + '\n'
            except IOError:
                return ''
    else:
        return ''

comment_re = re.compile(
    r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*)($)?',
    re.DOTALL | re.MULTILINE
)


def comment_replacer(match):
    start, mid, end = match.group(1, 2, 3)
    if mid is None:
        # single line comment
        return ''
    elif start is not None or end is not None:
        # multi line comment at start or end of a line
        return ''
    elif '\n' in mid:
        # multi line comment with line break
        return '\n'
    else:
        # multi line comment without line break
        return ' '


def remove_comments(text):
    return comment_re.sub(comment_replacer, text)


def remove_whitespace(text):
    return re.sub(r'\n\s*', '', text)