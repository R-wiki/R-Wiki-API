import sys
import json
from datetime import datetime
sys.path.append("..") 

from config.general import load_config

load_config("../config.ini")

from config.db import db


f = open("musiclib.json", "r", encoding="utf-8")
music_data_text = f.read()
f.close()
music_data = json.loads(music_data_text)
# print(music_data)

for old_music in music_data:
    new_music = {
        "name": old_music["name"],
        "music_type": old_music["musictype"],
        "language": old_music["language"],
        "solo": old_music["SOLO"],
        # "publish_time"
        # "platform"
        # "staff"
        "pv_mv": old_music["PV&MV"] if old_music["PV&MV"] != "无" else None,
        "album": old_music["album"],
        "note":  old_music["note"]
    }
    publish_time = datetime.strptime(old_music["publishtime"], "%Y年%m月%d日")
    new_music["publish_time"] = publish_time
    platform = {
        "netease": str(old_music["url"]) if old_music["platform"] in ("跨平台","网易") else None,
        "qq_music": None,
        "bilibili": None
    }
    new_music["platform"] = platform
    staff = []
    if old_music["composer"]:
        staff.append({"type":"作曲", "name":old_music["composer"]})
    if old_music["lyricist"]:
        staff.append({"type":"作词", "name":old_music["lyricist"]})
    if old_music["arranger"]:
        staff.append({"type":"编曲", "name":old_music["arranger"]})
    new_music["staff"] = staff
    new_music["show"] = 1
    print(new_music)
    db.music.insert_one(new_music)
    print()