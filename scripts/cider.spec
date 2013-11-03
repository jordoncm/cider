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
"""Spec file for building binaries."""


def data_files(source, target, paths):
    """Encapsulates the recursive data files tuple building."""
    import os

    def build_data_files_paths(source, target, paths):
        """Builds a file list based on a list of paths."""
        data_files = []

        for path in paths:
            if os.path.isfile(os.path.join(source, path)):
                data_files.append((
                    os.path.join(target, path),
                    os.path.join(target, path),
                    'DATA'
                ))
            elif os.path.isdir(os.path.join(source, path)):
                data_files.extend(build_data_files_paths(
                    os.path.join(source, path),
                    os.path.join(target, path),
                    os.listdir(os.path.join(source, path))
                ))

        return data_files

    return build_data_files_paths(source, target, paths)

DATA_FILES = data_files('', '', [
    'static',
    'templates',
    'configuration.json',
    'license.txt',
    'readme.md'
])

a = Analysis(
    ['server.py'],
    pathex=[os.path.dirname(__file__)],
    hiddenimports=[],
    hookspath=None,
    runtime_hooks=None
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries + DATA_FILES,
    a.zipfiles,
    a.datas,
    name='cider',
    debug=False,
    strip=None,
    upx=True,
    console=True
)
