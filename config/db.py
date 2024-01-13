import random
import string
import hashlib
from pymongo import MongoClient

from .general import CONFIG

client = MongoClient(CONFIG["DB"]["URL"])

db = client[CONFIG["DB"]["Database"]]

def get_password_hash(password: str):
    SECRET = CONFIG["DEFAULT"]["Secret"]
    result = hashlib.md5((password+SECRET).encode()).hexdigest()
    return result

admin_count = db.user.count_documents({"level":4})
if admin_count == 0:
    characters = string.ascii_letters + string.digits
    init_password = ''.join(random.choice(characters) for _ in range(8))
    password_hash = get_password_hash(init_password)
    db.user.insert_one({"username":"admin", "password_hash":password_hash, "level":4})
    print("No admin user detected.")
    print("New admin user is created, please login with username: admin and password: {}".format(init_password))