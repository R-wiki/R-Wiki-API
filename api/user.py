import random
import string
import hashlib
import jwt
from datetime import datetime, timedelta
from bson import ObjectId

from config.general import CONFIG
from config.db import db
from models.user import UserLoginRequest, UserInfoModel, CreateUserRequest, Level, NewUserModel
from fastapi import HTTPException


SECRET = CONFIG["DEFAULT"]["Secret"]

def get_password_hash(password: str):
    result = hashlib.md5((password+SECRET).encode()).hexdigest()
    return result

def get_jwt_by_user(user: UserLoginRequest):
    password_hash = get_password_hash(user.password)
    user_data = db.user.find_one({"username":user.username, "password_hash":password_hash})
    if user_data:
        jwt_payload = jwt.encode(
            {
                "id": str(user_data["_id"]),
                "exp": datetime.utcnow() + timedelta(days=1),
                "username":user_data["username"],
                "level":user_data["level"],
            }
            , SECRET)
        return jwt_payload
    else:
        raise HTTPException(40103, "Wrong username/password.")
    
def get_user_data_by_toekn(token: str):
    try:
        jwt_data = jwt.decode(token, SECRET, algorithms=["HS256"])
        return UserInfoModel(id=jwt_data["id"], username=jwt_data["username"], level=Level(jwt_data["level"]))
    except Exception as e:
        print(e)
        raise HTTPException(40104, "Invalid/outdated token.")
    
def update_password(user: UserInfoModel, password: str):
    password_hash = get_password_hash(password)
    db.user.update_one({"_id":ObjectId(user.id)}, {"$set":{"password_hash":password_hash}})

def create_user(new_user_info: CreateUserRequest):
    existing_user = db.user.find_one({"username":new_user_info.username})
    if existing_user:
        raise HTTPException(40206, "Username already exists.")
    characters = string.ascii_letters + string.digits
    init_password = ''.join(random.choice(characters) for _ in range(8))
    password_hash = get_password_hash(init_password)
    result = db.user.insert_one({"username":new_user_info.username, "password_hash":password_hash, "level":new_user_info.level})
    return NewUserModel(id=str(result.inserted_id), password=init_password)