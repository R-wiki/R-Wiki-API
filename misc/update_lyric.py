import sys
import os
import re
import json
from datetime import datetime
from bson import ObjectId
import requests
from openai import OpenAI
sys.path.append("..")

from config.general import load_config

load_config("../config.ini")

from config.db import db

def lyric_dumper(lyric):
    print("Loading from OpenAI...")
    client = OpenAI()
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "你是一个lrc文件处理工具，将收到的lrc字符串做处理为JSON格式数据，要求如下：1. 按照\\n分行；2. 去掉和歌词正文无关的行，如作词作曲信息，演奏者信息等，对唱提示等；3. 提取每行的时间标记和正文。时间标记需要删除方括号，如果有多个时间标记则解析为多行歌词，只需删除每句最后的标点符号。歌词正文需要删除歌手名或者男女对唱提示；4. 以JSON格式返回。格式为：{\"lyric_lines\":[{\"time_mark\":\"时间标记\",\"text\":\"正文\"}, ...]}，每句歌词解析为一个object，必须且只须要time_mark和text这两个key。",
            },
            {
                "role": "user",
                "content": lyric,
            }
        ],
        model="gpt-4o",
        response_format={ "type": "json_object" }
    )
    return json.loads(completion.choices[0].message.content)["lyric_lines"]

music_list_req = requests.get("https://api.yinlin.wiki/music/latest?size=5")
music_list = music_list_req.json()["data"]
for music in music_list[:]:
    existing_lyric = db.lyric.find_one({"music_id":ObjectId(music["id"])})
    if existing_lyric:
        print("Data exists, Pass.")
        continue
    music_info_req = requests.get("https://api.yinlin.wiki/music/detail?music_id="+music["id"])
    music_info = music_info_req.json()["data"]
    lyric_text = music_info["lyric"]
    print(lyric_text)
    if not lyric_text:
        print("No lyric, Pass.")
        continue
    while True:
        try:
            lyric_lines = lyric_dumper(lyric_text)
            insert_list = []
            for lyric_line in lyric_lines:
                print(lyric_line)
                insert_list.append({
                    "music_id"  : ObjectId(music["id"]),
                    "time_mark" : lyric_line["time_mark"],
                    "text"      : lyric_line["text"]
                })
            break
        except:
            print("----------Error retry----------")
    # print(insert_list)
    if insert_list and input() == "y":
        db.lyric.insert_many(insert_list)
    else:
        continue
