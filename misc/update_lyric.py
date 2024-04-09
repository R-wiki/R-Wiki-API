import sys
import os
import re
import json
from datetime import datetime
from bson import ObjectId
sys.path.append("..") 

from config.general import load_config

load_config("../config.ini")

from config.db import db

def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname, f

for full_name, file_name in findAllFile(".\\lyrics"):
    f = open(full_name, "r", encoding="utf-8")
    lrc_lines = f.readlines()
    print(file_name)
    file_id = file_name.split("_")[0]
    insert_list = []
    for line in lrc_lines:
        line = line.strip()
        if line == "":
            continue
        match_obj = re.match(r"^(\[[0-9\.:]+\])+(.*?)$", line)
        if not match_obj:
            continue
        match_items = match_obj.groups()
        time_marks = [i.strip("[]") for i in match_items[:-1]]
        text = match_items[-1]
        print(time_marks, text)
        if not text:
            print("skip")
            continue
        else:
            print("OK")
            for tm in time_marks:
                insert_list.append({
                    "music_id"  : ObjectId(file_id),
                    "time_mark" : tm,
                    "text"      : text
                })
    print(insert_list)
    if insert_list:
        db.lyric.insert_many(insert_list)