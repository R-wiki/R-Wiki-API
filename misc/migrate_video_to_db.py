import time
import sys
import json
from datetime import datetime
import re
import requests

sys.path.append("..") 

from config.general import load_config

load_config("../config.ini")

from config.db import db

f = open("videos.json", "r", encoding="utf-8")
video_data_text = f.read()
f.close()
video_data = json.loads(video_data_text)
# print(video_data)

header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}

for old_video in video_data[:]:
    old_video_url = old_video["url"]
    bvid = re.findall("(?<=bvid=).*?(?=&)", old_video_url)[0]
    cid = re.findall("(?<=cid=).*?(?=&)", old_video_url)[0]
    print(bvid, cid)
    bili_req = requests.get("https://api.bilibili.com/x/web-interface/view?bvid={}".format(bvid), headers = header)
    bili_data = bili_req.json()
    print(bili_data)
    new_video = {
        "name": bili_data["data"]["title"],
        "publish_time": datetime.fromtimestamp(bili_data["data"]["pubdate"]),
        "type": old_video["class"],
        "bvid": bvid,
        "cid": cid,
        "duration": bili_data["data"]["duration"],
        "show": True
    }
    db.video.insert_one(new_video)
    print(new_video)
    time.sleep(0.5)
