import configparser
from constants import *

CONFIGS = configparser.ConfigParser()
CONFIGS.read('settings.ini')

SEARCH_VECTOR_DICT = {}
