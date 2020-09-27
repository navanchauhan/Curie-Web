import configparser
import sys

iniConfig = configparser.ConfigParser()
iniConfig.read('config.ini')

try:
    iniConfig['DATABASE']
except KeyError:
    try:
        iniConfig.read("../config.ini")
    except KeyError:
        iniConfig.read("../../config.ini")