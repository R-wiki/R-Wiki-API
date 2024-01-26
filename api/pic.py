from bson import ObjectId

from fastapi import HTTPException

from config.db import db
from models.pic import PicItemModel, PicDetailModel

from .general import verify_object_id

def create_pic_item(pic_data:PicItemModel):
    pic_data_dict = pic_data.model_dump()
    pic_data_dict["show"] = False
    pic_id = pic_data_dict.get("id", None)
    del pic_data_dict["id"]
    if pic_id != None: # Update pic
        verify_object_id(pic_id)
        try:
            db.pic.update_one({"_id":ObjectId(pic_id)}, {"$set":pic_data_dict})
        except Exception as e:
            print(e)
            raise HTTPException(50101, "Database error.")
        return True
    else: # Create pic
        cursor = db.pic.find_one({"name":pic_data_dict["name"]})
        if cursor:
            raise HTTPException(40304, "Exists a pic with same name.")
        try:
            db.pic.insert_one(pic_data_dict)
        except Exception as e:
            print(e)
            raise HTTPException(50101, "Database error.")
        return True
    
def approve_pic(pic_id):
    verify_object_id(pic_id)
    try:
        db.pic.update_one({"_id":ObjectId(pic_id)}, {"$set":{"show":True}})
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return True

def decline_pic(pic_id):
    verify_object_id(pic_id)
    try:
        db.pic.delete_one({"_id":ObjectId(pic_id)})
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return True

def get_pic_list_by_query(query, page, size):
    try:
        count = db.pic.count_documents(query)
        cursor = db.pic.find(query).sort("date", -1).skip((page-1)*size).limit(size)
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    return cursor, count

def get_latest_pic_list(page,size):
    cursor, count = get_pic_list_by_query({"show": True}, page, size)
    return [PicItemModel(id=str(i["_id"]),**i) for i in cursor], count

def get_pending_pic_list(page,size):
    cursor, count = get_pic_list_by_query({"show": False}, page, size)
    return [PicItemModel(id=str(i["_id"]),**i) for i in cursor], count

def get_pic_list_by_filter(q, pic_type, year, month, page, size):
    query = {"show": True}
    if q:
        query["name"] = {"$regex":q}
    if pic_type:
        query["type"] = {"$in": pic_type}
    if year or month:
        query["$expr"] = {"$and": []}
    if year:
        query["$expr"]["$and"].append({
                "$in": [ {"$year": "$date" }, year ]
           })
    if month:
        query["$expr"]["$and"].append({
            "$in": [ {"$month": "$date" }, month ]
        })
    print(query)
    cursor, count = get_pic_list_by_query(query, page, size)
    return [PicItemModel(id=str(i["_id"]),**i) for i in cursor], count

def get_pic_detail(pic_id):
    verify_object_id(pic_id)
    try:
        cursor = db.pic.find_one({"_id":ObjectId(pic_id), "show":True})
    except Exception as e:
        print(e)
        raise HTTPException(50101, "Database error.")
    if not cursor:
        raise HTTPException(40301, "Music not exists.")
    # TODO: Get real pic urls here
    real_urls = cursor["pics"]
    return PicDetailModel(
        urls=real_urls,
        **cursor
    )