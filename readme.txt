Provides a web based file manager and collaborative IDE like code editor.

Requires Python to be installed in order to run. To start the server simply 
execute:

python server.py

This will start an HTTP server listening on port 3333. To access the interface 
point your browser to http://[your server ip]:3333/.

WARNING: This utility should only be used on computers with appropriate network 
security in place as it can allow users modify and execute code on the target 
system.

Configuration Details

You can modify the file configuration.json and set the following values:

basePathAdjustment    : Allows adjustment of the path that cider's file manager 
                        and editor are locked to for all browsing and editing. 
                        All values must be set in respect to cider's location.
                        By default it will be set to '~' to allow editing the 
                        users home folder.

cookieSecret          : String of text to be used as the key to encrypt secure 
                        cookies. Should be set to something private and unique 
                        for production instances.

dropboxKey            : Dropbox API key as provided from Dropbox. Needs to be 
                        set for Dropbox support. See 
                        https://www.dropbox.com/developers for details.

dropboxSecret         : Dropbox API secret as provided from Dropbox. Needs to 
                        be set for Dropbox support. See 
                        https://www.dropbox.com/developers for details.

enableLocalFileSystem : Flag to enable/disable browsing and editing of local 
                        files. Defaults to true.

enableSFTP            : Flag to enable/disable SFTP support. Defaults to true. 
                        NOTE: This feature will also be disabled if dependent 
                        Python libraries are missing from system (see below).

port                  : The port for Cider to listen for requests on. Default 
                        port is 3333.

suppressBrowser       : Set true to prevent a browser form opening the homepage 
                        on startup.

terminalLink          : A full URL to a web based console login (i.e. 
                        shellinabox). If set, an icon will show on the homepage 
                        and link to the console login. You may include the 
                        string '[host]' in your link and it will be replaced 
                        with the requesting host.

Be sure to keep the JSON in the file valid otherwise it will ignore your 
settings and take defaults.

Note About SFTP/SSH Support

SFTP/SSH support uses the non-standard Python libraries pysftp, paramiko and 
pycrypto. None of these are bundled within Cider (unlike tornado). These 
libraries will need to be installed in order to use SFTP/SSH support in Cider. 
pysftp, paramiko and pycrypto are available in PyPI. This does not apply to the 
bundled Mac version as Python and all libraries are bundled in the build.

- - - - -

This work is copyright 2011 - 2012 Jordon Mears. All rights reserved.

This file is part of Cider.

Cider is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cider is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cider.  If not, see <http://www.gnu.org/licenses/>.