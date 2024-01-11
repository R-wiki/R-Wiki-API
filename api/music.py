from bson import ObjectId

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
        pass
    else: # Create music
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
        cursor = db.music.find(query).sort("time", -1).skip((page-1)*size).limit(size)
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return cursor

def get_latest_music_list(page=1,size=10):
    cursor = get_music_list_by_query({"show": True}, page, size)
    return [MusicInfoModel(id=str(i["_id"]),**i) for i in cursor]

def get_pending_music_list(page=1,size=10):
    cursor = get_music_list_by_query({"show": False}, page, size)
    return [MusicInfoModel(id=str(i["_id"]),**i) for i in cursor]

def get_music_list_by_filter(album, solo, platform, language, page=1, size=10):
    query = {"show": True}
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
    cursor = get_music_list_by_query(query, page, size)
    return [MusicInfoModel(id=str(i["_id"]),**i) for i in cursor]

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
    return MusicDetailModel(
        id          = str(cursor["_id"]), 
        cover_url   = cover_url, 
        play_url    = play_url,
        lyric       = lyric,
        **cursor
    )
    
