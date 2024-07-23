import sys
import json
from datetime import datetime
sys.path.append("..") 

from config.general import load_config

load_config("../config.ini")

from config.db import db

f = open("picurl.json", "r", encoding="utf-8")
pic_data_text = f.read()
f.close()
pic_data = json.loads(pic_data_text)
# print(pic_data)

for old_pic in pic_data[:]:
    new_pic = {
        "name": old_pic["group"]["name"],
        "date": datetime.strptime(old_pic["group"]["date"], "%Y%m%d"),
        "type": old_pic["type"],
        "pics": [i["url"] for i in old_pic["group"]["urls"]],
        "cover": old_pic["group"]["urls"][0]["url"],
        "note": "",
        "show": 1
    }
    db.pic.insert_one(new_pic)
    print(new_pic)