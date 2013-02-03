"""Module containing and processing command line options."""

import optparse

PARSER = optparse.OptionParser()
PARSER.add_option('-c', '--config', help='Path to configuration file.')
OPTIONS = PARSER.parse_args()[0]

def get(key, default = None):
    """Retrieve an options by its key."""
    return getattr(OPTIONS, key, default)
