from bson import ObjectId
import requests

from fastapi import HTTPException
import oss2

from config.general import CONFIG
from config.db import db
from models.pic import PicItemModel, PicDetailModel, SinglePicModel

from .general import verify_object_id

OSS_AUTH = oss2.Auth(CONFIG["OSS"]["AccessKey_ID"], CONFIG["OSS"]["AccessKey_Secret"])
OSS_BUCKET = oss2.Bucket(OSS_AUTH, CONFIG["OSS"]["Endpoint"], CONFIG["OSS"]["Bucket"])

def get_signed_pic_url(path, thumbnail=True, size=0, expire=600):
    if "http" in path:
        return path
    if thumbnail:
        size = CONFIG["PIC"]["Thumbnail_Size"]
    if size !=0:
        style = "image/resize,m_lfit,w_{0},h_{0}".format(size)
    else:
        style = ""
    url = OSS_BUCKET.sign_url('GET', path, expire, params={'x-oss-process': style})
    return url

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
    pic_item_list = []
    for pic_item in cursor:
        pic_item["id"] = str(pic_item["_id"])
        pic_item["cover"] = get_signed_pic_url(pic_item["pics"][0], thumbnail=True)
        pic_item_list.append(PicItemModel(**pic_item))
    return pic_item_list, count

def get_pending_pic_list(page,size):
    cursor, count = get_pic_list_by_query({"show": False}, page, size)
    pic_item_list = []
    for pic_item in cursor:
        pic_item["id"] = str(pic_item["_id"])
        pic_item["cover"] = get_signed_pic_url(pic_item["pics"][0], thumbnail=True)
        pic_item_list.append(PicItemModel(**pic_item))
    return pic_item_list, count

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
    pic_item_list = []
    for pic_item in cursor:
        pic_item["id"] = str(pic_item["_id"])
        pic_item["cover"] = get_signed_pic_url(pic_item["pics"][0], thumbnail=True)
        pic_item_list.append(PicItemModel(**pic_item))
    return pic_item_list, count

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
    cursor["cover"] = get_signed_pic_url(cursor["pics"][0], thumbnail=True)
    real_urls = [get_signed_pic_url(i, thumbnail=True) for i in cursor["pics"]]
    return PicDetailModel(
        urls=real_urls,
        **cursor
    )

def get_original_pic(path):
    real_url = get_signed_pic_url(path, thumbnail=False, expire=60)
    return SinglePicModel(
        id      = "",
        set_id  = "",
        path    = path,
        url     = real_url
    )

def ai_search(q):
    vector_api_url = CONFIG["EXTERNAL_API"]["TEXT_VECTOR_API"]
    vector_api_token = CONFIG["EXTERNAL_API"]["TEXT_VECTOR_API_TOKEN"]
    if vector_api_url:
        try:
            vector_req = requests.get(vector_api_url + "?q={}&token={}".format(q, vector_api_token), timeout=30)
            vector_data = vector_req.json()["vector"]
            query_result = db.pic_vector.aggregate([
                {
                    '$vectorSearch': {
                        'queryVector': vector_data, 
                        'path': 'vector', 
                        'numCandidates': 10, 
                        'index': 'vector_index', 
                        'limit': 5, 
                        'filter': {}
                    }
                }, {
                    '$project': {
                        '_id': 1, 
                        'set_id': 1, 
                        'path': 1
                    }
                }
            ])
            single_pic_list = []
            for pic in query_result:
                single_pic_list.append(SinglePicModel(
                    id      = str(pic["_id"]),
                    set_id  = str(pic["set_id"]),
                    path    = pic["path"],
                    url     = get_signed_pic_url(pic["path"], thumbnail=True)
                ))
            return single_pic_list, len(single_pic_list)
        except:
            return [], 0
    else:
        return [], 0