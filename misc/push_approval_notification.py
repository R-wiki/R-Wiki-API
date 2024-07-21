import os
import requests
import json
import time

username = os.environ.get("RWIKI_API_USERNAME", "")
password = os.environ.get("RWIKI_API_PASSWORD", "")
wechat_key = os.environ.get("WECHAT_KEY", "")

user_token_request = requests.post(
    "https://api.yinlin.wiki/user/login",
    json={
        "username": username,
        "password": password
        }
    )
user_token = user_token_request.json()["data"]["token"]
print(user_token)

checklist_requset = requests.get( 
    "https://api.yinlin.wiki/external/checklist",
    headers={"x-token":user_token}
)
checklist = checklist_requset.json()["data"]
print(checklist)
for item in checklist:
    push_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + wechat_key
    content = "有新的银临WIKI API更新需要批准：\n" + \
                "类型：{}\n" + \
                "{}\n\n" + \
                "在30分钟内点击以下链接：\n" + \
                "[批准](https://api.yinlin.wiki/external/approve?token={})  [拒绝](https://api.yinlin.wiki/external/decline?token={})"
    content = content.format(
        item["item_type"],
        item["content"],
        item["token"],
        item["token"]
    )
    
    push_payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    a = requests.post(push_url,data=json.dumps(push_payload),timeout=10)
    if a.json()["errcode"] == 0:
        print("OK")
    else:
        print("Status {}".format(a.json()["errmsg"]))
    time.sleep(0.5)
