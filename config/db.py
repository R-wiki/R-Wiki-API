from pymongo import MongoClient

from .general import CONFIG

client = MongoClient(CONFIG["DB"]["URL"])

db = client[CONFIG["DB"]["Database"]]