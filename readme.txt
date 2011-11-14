Provides a web based file manager and IDE like code editor.

Requires Python to be installed in order to run. To start the server simply 
execute:

python server.py

This will start an HTTP server listening on port 3333. To access the interface 
point your browser to http://[your server ip]:3333/.

WARNING: This utility should only be used on servers with appropriate network 
security in place as it can allow users modify and execute code on the target 
system.

Configuration Details

You can modify the file configuration.json and set the following values:

basePathAdjustment : Allows adjustment of the path that cider's file manager 
                     and editor are locked to for all browsing and editing. All 
                     values must be set in respect to cider's location. By 
                     default it will be set to '..' to allow editing one 
                     directory above cider's location.

terminalLink       : A full URL to a web based console login (i.e. shellinabox). 
                     If set, an icon will show on the homepage and link to the 
                     console login. You may include the string '[host]' in your 
                     link and it will be replaced with the requesting host.

Be sure to keep the JSON in the file valid otherwise it will ignore your 
settings and take defaults.

This work is copyright Jordon Mears. All rights reserved. See license.txt for 
details.