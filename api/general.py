from bson import ObjectId
from datetime import datetime

from fastapi import HTTPException

from config.db import db

def verify_object_id(object_id):
    try:
        _ = ObjectId(object_id)
    except:
        raise HTTPException(40201, "Invalid ID.")
    
def user_action_log(username, type, action, target_id=None, info=""):
    if target_id:
        target_id = ObjectId(target_id)
    db.log.insert_one({
        "username": username,
        "type": type,
        "action": action,
        "target_id": target_id,
        "info": info,
        "datetime": datetime.now()
    })
