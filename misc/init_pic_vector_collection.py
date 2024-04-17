import sys
import json
import bson
from datetime import datetime
sys.path.append("..") 

from config.general import load_config

load_config("../config.ini")

from config.db import db
# from api.pic import get_latest_pic_list

# pics ,_ = get_latest_pic_list(1,200)
# 
# for pic in pics:
#     for pic_dir in pic.pics:
#         print(pic_dir)
#         db.pic_vector.insert_one({
#             "set_id": bson.ObjectId(pic.id),
#             "path": pic_dir
#         })

with open("data.json", "r") as f:
    data = json.loads(f.read())
for i in data:
    print(i)
    db.pic_vector.update_one(
        {"path":i},
        {"$set":{"vector": data[i]}}
    )