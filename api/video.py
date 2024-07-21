from functools import lru_cache
from datetime import datetime
import requests
from bson import ObjectId

from fastapi import HTTPException

from config.db import db
from models.video import VideoItemModel, VideoDetailModel

from .general import verify_object_id

def create_video_item(video_data:VideoItemModel):
    video_data_dict = video_data.model_dump()
    video_data_dict["show"] = False
    video_id = video_data_dict.get("id", None)
    del video_data_dict["id"]
    if video_id != None: # Update video
        verify_object_id(video_id)
        try:
            db.video.update_one({"_id":ObjectId(video_id)}, {"$set":video_data_dict})
        except Exception as e:
            print(e)
            raise HTTPException(50101, "Database error.")
        return True
    else: # Create video
        cursor = db.video.find_one({"name":video_data_dict["name"]})
        if cursor:
            raise HTTPException(40304, "Exists a video with same name.")
        try:
            db.video.insert_one(video_data_dict)
        except Exception as e:
            print(e)
            raise HTTPException(50101, "Database error.")
        return True
    
def approve_video(video_id):
    verify_object_id(video_id)
    try:
        result = db.video.update_one({"_id":ObjectId(video_id)}, {"$set":{"show":True}})
        if result.modified_count == 1:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return True

def decline_video(video_id):
    verify_object_id(video_id)
    try:
        result = db.video.delete_one({"_id":ObjectId(video_id), "show":False})
        if result.deleted_count == 1:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")

def get_video_list_by_query(query, page, size):
    try:
        count = db.video.count_documents(query)
        cursor = db.video.find(query).sort("publish_time", -1).skip((page-1)*size).limit(size)
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return cursor, count

def get_latest_video_list(page,size):
    cursor, count = get_video_list_by_query({"show": True}, page, size)
    return [VideoItemModel(id=str(i["_id"]),**i) for i in cursor], count

def get_pending_video_list(page,size):
    cursor, count = get_video_list_by_query({"show": False}, page, size)
    return [VideoItemModel(id=str(i["_id"]),**i) for i in cursor], count

def get_video_list_by_filter(q, duration, video_type, year, month, page, size):
    duration_map = {
        "s": {"duration":{"$lte": 10*60 }},
        "m": {"duration":{"$gte": 10*60, "$lte": 30*60}},
        "l": {"duration":{"$gte": 30*60 }}
    }

    query = {"show": True}
    if q:
        query["name"] = {"$regex":q}
    if duration:
        query["$or"] = []
        for d in duration:
            if d in duration_map:
                query["$or"].append(duration_map[d])
    if video_type:
        query["type"] = {"$in": video_type}
    if year or month:
        query["$expr"] = {"$and": []}
    if year:
        query["$expr"]["$and"].append({
                "$in": [ {"$year": "$publish_time" }, year ]
           })
    if month:
        query["$expr"]["$and"].append({
            "$in": [ {"$month": "$publish_time" }, month ]
        })
    print(query)
    cursor, count = get_video_list_by_query(query, page, size)
    return [VideoItemModel(id=str(i["_id"]),**i) for i in cursor], count

def get_video_detail(video_id):
    verify_object_id(video_id)
    try:
        cursor = db.video.find_one({"_id":ObjectId(video_id), "show":True})
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    if not cursor:
        raise HTTPException(40301, "Music not exists.")
    return VideoDetailModel(
        url="//www.bilibili.com/blackboard/html5mobileplayer.html?bvid={}&cid={}".format(cursor["bvid"],cursor["cid"]),
        **cursor
    )

def create_video_by_bvid(bvid, video_type=""):
    BILI_DETAIL_URL = "https://api.bilibili.com/x/web-interface/view?bvid={}"
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    try:
        bili_req = requests.get(BILI_DETAIL_URL.format(bvid), headers = header)
        bili_data = bili_req.json()
        new_video = VideoItemModel(
            name            = bili_data["data"]["title"],
            publish_time    = datetime.fromtimestamp(bili_data["data"]["pubdate"]),
            type            = video_type,
            bvid            = bvid,
            cid             = str(bili_data["data"]["cid"]),
            duration        = bili_data["data"]["duration"],
            show            = False
        )
    except Exception as e:
        raise HTTPException(50102, "External API Error: Bilibili: "+ str(e))
    create_video_item(new_video)
    return True
