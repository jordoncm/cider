import getpass
import json
import os
import string
import sys

try:
    __file__
except NameError:
    if hasattr(sys, 'frozen') and sys.frozen in ('windows_exe', 'console_exe'):
        __file__ = os.path.dirname(os.path.abspath(sys.executable))

def getConfigurationValue(key, default = None):
    try:
        return json.loads(open(os.path.join(
            os.path.dirname(__file__),
            'configuration.json'
        )).read())[key]
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