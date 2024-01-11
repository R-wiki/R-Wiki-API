from bson import ObjectId

from fastapi import HTTPException

def verify_object_id(object_id):
    try:
        _ = ObjectId(object_id)
    except:
        raise HTTPException(40201, "Invalid ID.")