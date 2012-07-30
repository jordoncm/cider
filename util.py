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
