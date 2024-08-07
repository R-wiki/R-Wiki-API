from bson import ObjectId
from datetime import datetime, timedelta

from fastapi import HTTPException
import jwt

from config.general import CONFIG
from config.db import db

from models.external import ChecklistItemModel

import api.music as MusicApi
import api.pic as PicApi
import api.video as VideoApi
import api.activity as ActivityApi

SECRET = CONFIG["DEFAULT"]["Secret"]

def generate_jwt(item_type, item_id):
    jwt_payload = jwt.encode(
        {
            "item_type": item_type,
            "item_id": item_id,
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        , SECRET)
    return jwt_payload

def verify_jwt(token=""):
    try:
        jwt_data = jwt.decode(token, SECRET, algorithms=["HS256"])
        print(jwt_data)
        return jwt_data["item_type"], jwt_data["item_id"]
    except Exception as e:
        print(e)
        raise HTTPException(40104, "Invalid/expired token.")

def get_checklist():
    checklist = []
    pending_musics, _ = MusicApi.get_pending_music_list(1, 50)
    for music in pending_musics:
        checklist.append({
            "item_id": music.id,
            "item_type": "music",
            "content": music.model_dump_json(indent=2),
            "token": generate_jwt("music", music.id,)
        })
    pending_pics, _ = PicApi.get_pending_pic_list(1, 50)
    for pic in pending_pics:
        checklist.append({
            "item_id": pic.id,
            "item_type": "pic",
            "content": pic.model_dump_json(indent=2),
            "token": generate_jwt("pic", pic.id)
        })
    pending_videos, _ = VideoApi.get_pending_video_list(1, 50)
    for video in pending_videos:
        checklist.append({
            "item_id": video.id,
            "item_type": "video",
            "content": video.model_dump_json(indent=2),
            "token": generate_jwt("video", video.id)
        })
    pending_activities, _ = ActivityApi.get_pending_activity_list(1, 50)
    for activity in pending_activities:
        checklist.append({
            "item_id": activity.id,
            "item_type": "activity",
            "content": activity.model_dump_json(indent=2),
            "token": generate_jwt("activity", activity.id)
        })

    return [ChecklistItemModel(**i) for i in checklist], len(checklist)

def approve(item_type, item_id):
    if item_type == "music":
        return MusicApi.approve_music(item_id)
    elif item_type == "pic":
        return PicApi.approve_pic(item_id)
    elif item_type == "video":
        return VideoApi.approve_video(item_id)
    elif item_type == "activity":
        return ActivityApi.approve_activity(item_id)
    else:
        return False

def decline(item_type, item_id):
    if item_type == "music":
        return MusicApi.decline_music(item_id)
    elif item_type == "pic":
        return PicApi.decline_pic(item_id)
    elif item_type == "video":
        return VideoApi.decline_video(item_id)
    elif item_type == "activity":
        return ActivityApi.decline_activity(item_id)
    else:
        return False