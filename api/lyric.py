from fastapi import HTTPException

from config.general import CONFIG
from config.db import db

from models.lyric import LyricLineModel, MusicLyricModel

def search_lyric(q=""):
    if len(q) < 2:
        raise HTTPException(40305, "Query string should be longer than 2.")
    else:
        query_result = db.lyric.aggregate([
            {
                '$sort': {
                    'time_mark': 1
                }
            }, {
                '$match': {
                    'text': {
                        '$regex': q
                    }
                }
            }, {
                '$group': {
                    '_id': '$music_id', 
                    'lyrics': {
                        '$push': {
                            'time_mark': '$time_mark', 
                            'text': '$text'
                        }
                    }
                }
            }, {
                '$lookup': {
                    'from': 'music', 
                    'localField': '_id', 
                    'foreignField': '_id', 
                    'as': 'data'
                }
            }, {
                '$sort': {
                    'data.publish_time': -1
                }
            }
        ])
        lyric_data = []
        for music_lyric in query_result:
            lyric_data.append(
                MusicLyricModel(
                    music_id = str(music_lyric["_id"]),
                    name     = music_lyric["data"][0]["name"],
                    lyrics   = [LyricLineModel(time_mark=lyric_item["time_mark"], text=lyric_item["text"]) for lyric_item in music_lyric["lyrics"]]
                )
            )
        return lyric_data, len(lyric_data)