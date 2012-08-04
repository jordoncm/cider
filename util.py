import getpass
import json
import os
import string
import sys


def getConfigurationValue(key, default = None):
    try:
        return json.loads(open(
            'configuration.json'
        ).read())[key]
    except:
        return default


def isTextFile(file):
    sample = open(file).read(512)
    if not sample:
        return True
    if '\0' in sample:
        return False
    text = sample.translate(
        string.maketrans('', ''),
        ''.join(map(chr, range(32, 127)) + list('\n\r\t\b'))
    )
    if len(text) / len(sample) > 0.30:
        return False
    return True


def getBasePathAdjustment():
    BASE_PATH_ADJUSTMENT = getConfigurationValue('basePathAdjustment')
    if BASE_PATH_ADJUSTMENT == None:
        BASE_PATH_ADJUSTMENT = '..'
    elif BASE_PATH_ADJUSTMENT == '~':
        if 'darwin' in sys.platform:
            BASE_PATH_ADJUSTMENT = '/Users/' + getpass.getuser()
        elif 'win' in sys.platform:
            BASE_PATH_ADJUSTMENT = 'C:\\Users\\' + getpass.getuser()
        else:
            BASE_PATH_ADJUSTMENT = '/home/' + getpass.getuser()
    return BASE_PATH_ADJUSTMENT


def getMode(ext):
    mode, tabWidth, markup = getModeTabWidthMarkup(ext)
    return mode


def getModeTabWidthMarkup(ext):
    tabWidth = 4
    markup = False
    
    if ext == 'c' or ext == 'cpp' or ext == 'h' or ext == 'hpp':
        mode = 'c_cpp'
    elif ext == 'clj':
        mode = 'clojure'
    elif ext == 'coffee':
        mode = 'coffee'
    elif ext == 'cfc' or ext == 'cfm':
        mode = 'coldfusion'
    elif ext == 'cs':
        mode = 'csharp'
    elif ext == 'css':
        mode = 'css'
    elif ext == 'go':
        mode = 'go'
    elif ext == 'groovy':
        mode = 'groovy'
    elif ext == 'hx':
        mode = 'haxe'
    elif ext == 'htm' or ext == 'html' or ext == 'mustache' or ext == 'tpl' or ext == 'shtml':
        mode = 'html'
        tabWidth = 2
        markup = True
    elif ext == 'java':
        mode = 'java'
    elif ext == 'js':
        mode = 'javascript'
    elif ext == 'json':
        mode = 'json'
    elif ext == 'tex':
        mode = 'latex'
    elif ext == 'less':
        mode = 'less'
    elif ext == 'liquid':
        mode = 'liquid'
    elif ext == 'lua':
        mode = 'lua'
    elif ext == 'markdown' or ext == 'mdown' or ext == 'mdown' or ext == 'md' or ext == 'mkd' or ext == 'mkdn':
        mode = 'markdown'
    elif ext == 'ocaml' or ext == 'ml' or ext == 'mli':
        mode = 'ocaml'
    elif ext == 'pl' or ext == 'pm' or ext == 't':
        mode = 'perl'
    elif ext == 'pgsql':
        mode = 'pgsql'
    elif ext == 'php' or ext == 'inc' or ext == 'phtml' or ext == 'phps':
        mode = 'php'
    elif ext == 'ps1':
        mode = 'powershell'
    elif ext == 'py' or ext == 'pyw':
        mode = 'python'
    elif ext == 'rb' or ext == 'rbw':
        mode = 'ruby'
    elif ext == 'scad':
        mode = 'scad'
    elif ext == 'scala':
        mode = 'scala'
    elif ext == 'scss':
        mode = 'scss'
    elif ext == 'sh':
        mode = 'sh'
    elif ext == 'sql':
        mode = 'sql'
    elif ext == 'svg':
        mode = 'svg'
        tabWidth = 2
        markup = True
    elif ext == 'textile':
        mode = 'textile'
    elif ext == 'xml' or ext == 'kml':
        mode = 'xml'
        tabWidth = 2
        markup = True
    elif ext == 'xq' or ext == 'xqy' or ext == 'xquery':
        mode = 'xquery'
    else:
        mode = 'text'
    
    return mode, tabWidth, markup


def getTabWidth(ext):
    mode, tabWidth, markup = getModeTabWidthMarkup(ext)
    return tabWidth


def isMarkup(ext):
    mode, tabWidth, markup = getModeTabWidthMarkup(ext)
    return markup