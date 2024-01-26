from functools import lru_cache
from bson import ObjectId
import requests

from fastapi import HTTPException

from config.db import db
from models.music import MusicInfoModel, MusicDetailModel

from .general import verify_object_id

def create_music_item(music_data:MusicInfoModel):
    music_data_dict = music_data.model_dump()
    music_data_dict["show"] = False
    music_id = music_data_dict.get("id", None)
    del music_data_dict["id"]
    if music_id != None: # Update music
        verify_object_id(music_id)
        try:
            db.music.update_one({"_id":ObjectId(music_id)}, {"$set":music_data_dict})
        except Exception as e:
            print(e)
            raise HTTPException(50101, "Database error.")
        return True
    else: # Create music
        cursor = db.music.find_one({"name":music_data_dict["name"]})
        if cursor:
            raise HTTPException(40304, "Exists a music with same name.")
        try:
            db.music.insert_one(music_data_dict)
        except Exception as e:
            print(e)
            raise HTTPException(50101, "Database error.")
        return True

def approve_music(music_id):
    verify_object_id(music_id)
    try:
        db.music.update_one({"_id":ObjectId(music_id)}, {"$set":{"show":True}})
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return True

def decline_music(music_id):
    verify_object_id(music_id)
    try:
        db.music.delete_one({"_id":ObjectId(music_id)})
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return True

def get_music_list_by_query(query, page, size):
    try:
        count = db.music.count_documents(query)
        cursor = db.music.find(query).sort("publish_time", -1).skip((page-1)*size).limit(size)
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return cursor, count

def get_latest_music_list(page,size):
    cursor, count = get_music_list_by_query({"show": True}, page, size)
    return [MusicInfoModel(id=str(i["_id"]),**i) for i in cursor], count

def get_pending_music_list(page,size):
    cursor, count = get_music_list_by_query({"show": False}, page, size)
    return [MusicInfoModel(id=str(i["_id"]),**i) for i in cursor], count

def get_music_list_by_filter(q, album, solo, platform, language, page, size):
    query = {"show": True}
    if q:
        query["name"] = {"$regex":q}
    if album:
        query["album"] = {"$in": album}
    if solo:
        query["solo"] = {"$in": solo}
    if platform:
        platform_query = []
        for p in platform:
            platform_query.append({"platform."+p:{"$ne":None}})
        query["$or"] = platform_query
    if language:
        query["language"] = {"$in": language}
    print(query)
    cursor, count = get_music_list_by_query(query, page, size)
    return [MusicInfoModel(id=str(i["_id"]),**i) for i in cursor], count

@lru_cache(maxsize=64)
def get_netease_detail(netease_id):
    cover_url = ""
    play_url  = ""
    lyric     = ""
    # Play URL
    play_url  = "https://music.163.com/song/media/outer/url?id={}".format(netease_id)
    # Cover and Lyric
    try:
        img_req = requests.get('http://music.163.com/api/song/detail/?id={}&ids=%5B{}%5D'.format(netease_id, netease_id), timeout=5)
        img_json = img_req.json()
        cover_url = img_json["songs"][0]["album"]["picUrl"]+"?param=300y300"

        lrc_req = requests.get('http://music.163.com/api/song/media?id={}'.format(netease_id), timeout=5)
        lrc_json = lrc_req.json()
        lyric = lrc_json["lyric"]
    except Exception as e:
        print("Error when get music info in netease:", str(e))
    return cover_url, play_url, lyric

@lru_cache(maxsize=64)
def try_search_in_kugou(music_name):
    cover_url = ""
    play_url  = ""
    lyric     = ""

    header = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"}
    music_search_url = "http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={}&page=1&pagesize=10&showtype=1"
    music_info_url = "http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={}"
    session = requests.Session()
    try:
        search_req = session.get(music_search_url.format(music_name+ " 银临"), headers=header, timeout=5)
        search_data = search_req.json()
        possible_hash = ""
        for possible_music in search_data["data"]["info"]:
            if "银临" in possible_music["singername"]:
                possible_hash = possible_music["320hash"]
                break
        info_req = session.get(music_info_url.format(possible_hash), headers=header, timeout=5)
        info_data = info_req.json()
        cover_url = info_data["album_img"].replace("{size}", "400")
        play_url = info_data["url"]
    except Exception as e:
        print("Error when get music info in kugou:", str(e))
    return cover_url, play_url, lyric

def get_music_detail(music_id):
    verify_object_id(music_id)
    try:
        cursor = db.music.find_one({"_id":ObjectId(music_id), "show":True})
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    if not cursor:
        raise HTTPException(40301, "Music not exists.")
    # TODO: Get cover url, play url, lyric here
    cover_url = ""
    play_url  = ""
    lyric     = ""
    if cursor["platform"]["netease"] != None: 
        cover_url ,play_url, lyric = get_netease_detail(cursor["platform"]["netease"])
    else:
        cover_url ,play_url, lyric = try_search_in_kugou(cursor["name"])
    return MusicDetailModel(
        id          = str(cursor["_id"]), 
        cover_url   = cover_url, 
        play_url    = play_url,
        lyric       = lyric,
        **cursor
    )
    