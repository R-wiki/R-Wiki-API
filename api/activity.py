from bson import ObjectId

from fastapi import HTTPException

from config.general import CONFIG
from config.db import db
from models.activity import ActivityModel, ActivityListResponse

from .general import verify_object_id
from .pic import get_signed_pic_url

def create_activity_item(activity_data: ActivityModel):
    activity_data_dict = activity_data.model_dump()
    activity_data_dict["show"] = 0
    activity_id = activity_data_dict.get("id", None)
    del activity_data_dict["id"]
    if activity_id != None: # Update music
        verify_object_id(activity_id)
        try:
            db.activity.update_one({"_id":ObjectId(activity_id)}, {"$set":activity_data_dict})
        except Exception as e:
            print(e)
            raise HTTPException(50101, "Database error.")
        return True
    else:
        cursor = db.activity.find_one({"name":activity_data_dict["name"]})
        if cursor:
            raise HTTPException(40304, "Exists a activity with same name.")
        try:
            db.activity.insert_one(activity_data_dict)
        except Exception as e:
            print(e)
            raise HTTPException(50101, "Database error.")
        return True

def approve_activity(activity_id):
    verify_object_id(activity_id)
    try:
        result = db.activity.update_one({"_id":ObjectId(activity_id), "show":0}, {"$set":{"show":1}})
        if result.modified_count == 1:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")

def decline_activity(activity_id):
    verify_object_id(activity_id)
    try:
        result = db.activity.update_one({"_id":ObjectId(activity_id), "show":0}, {"$set":{"show":-1}})
        if result.modified_count == 1:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")

def get_activity_list_by_query(query, page, size):
    try:
        count = db.activity.count_documents(query)
        cursor = db.activity.find(query).sort("publish_time", -1).skip((page-1)*size).limit(size)
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return cursor, count

def get_latest_activity_list(page, size):
    cursor, count = get_activity_list_by_query({"show": 1}, page, size)
    result = []
    for item in cursor:
        temp_item = ActivityModel(
            id = str(item["_id"]),
            **item
        )
        temp_item.pics = [get_signed_pic_url(i) for i in item["pics"]]
        result.append(temp_item)
        
    return result, count

def get_pending_activity_list(page, size):
    cursor, count = get_activity_list_by_query({"show": 0}, page, size)
    return [ActivityModel(id=str(i["_id"]),**i) for i in cursor], count