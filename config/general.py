import os
import configparser

CONFIG = {}

def load_config(path):
    global CONFIG
    if not os.path.exists(path):
        print("PLEASE CREATE CONFIG FILE config.ini")
        exit()
    CONFIG = configparser.ConfigParser()
    CONFIG.read(path)