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

with open("update_pic_data.json", "r") as f:
    data = json.loads(f.read())

pic_type_map = {
    "life": "生活照",
    "live": "现场",
    "artistic": "写真",
    "screenshot":"截图",
    "others":"其他"
}

for i in data:
    print(i)
    pic_info_arr = i.split("/")
    pic_type = pic_type_map.get(pic_info_arr[1], "其他")
    album_name = pic_info_arr[2]
    album_date_str = album_name.split("_")[0]
    if pic_type == "生活照":
        album_date = datetime(int(album_date_str))
    else:
        album_date = datetime.strptime(album_date_str, '%Y%m%d')
    file_path = pic_info_arr[3]
    print(pic_type, album_name, file_path)
    update_album = db.pic.find_one(
        {"type": pic_type, "name": album_name}
    )
    if update_album:
        db.pic.update_one(
            {"type": pic_type, "name": album_name},
            {"$addToSet":{"pics":i}}
        )
    else:
        db.pic.insert_one({
            "type"  : pic_type,
            "name"  : album_name,
            "date"  : album_date,
            "pics"  : [ i ],
            "cover" : i,
            "note"  : "",
            "show"  : 0
        })
        update_album = db.pic.find_one(
            {"type": pic_type, "name": album_name}
        )
    # Update Vector Collection
    print(update_album["_id"])
    db.pic_vector.insert_one({
        "set_id": update_album["_id"],
        "path"  : i,
        "vector": data[i]
    })