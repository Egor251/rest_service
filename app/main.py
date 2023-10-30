from typing import List
import asyncio
from fastapi import FastAPI
import uvicorn
from data_structure import *
import motor.motor_asyncio
from email_sender import Email_send
from bson.objectid import ObjectId
import time
import platform
import exrex
from pymongo import ReplaceOne
from dotenv import load_dotenv
import os

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # На всякий случай чтобы избежать проблем в среде windows

load_dotenv()
path = "settings.ini"

port = int(os.environ.get("PORT"))
my_password = os.environ.get("PASSWORD")
test_email = os.environ.get("EMAIL")
DB_URL = os.environ.get("DB_URL")

app = FastAPI()

cluster = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)  # Подключение к БД
collection = cluster.userdb.test

# Пример записи в базе
doc = {"user_id": ObjectId('123456789012345678901234'),
                "notifications": [
            {'target_id': ObjectId('123456789012345678901234'),
                'timestamp': 1698373379,
                "key": "new_message",
                "is_new": True,
                "data":
                    {"some": "thing"}}]}


async def replace_one(nosql, nosql2):
    request = [ReplaceOne(nosql, nosql2, upsert=True)]
    await collection.bulk_write(request)


async def insert(nosql):
    await collection.insert_one(nosql)


async def update(nosql1, nosql2):
    await collection.update_one(nosql1, nosql2)


async def do_find(nosql=None):

    cursor = collection.find(nosql)
    total = await cursor.to_list(length=100)

    return total


async def gather(func):
    result = await asyncio.gather(func)
    return result


@app.get("/")
def read_root():
    return {"Use /create, /list or /read"}


@app.post("/create")
async def create(query: List[CreateCom]):

    for item in query:  # Парсим POST запрос
        user_id = item.user_id
        target_id = item.target_id
        if target_id is None:  # Если target_id имеет значение None сгенерируем значение сами
            target_id = exrex.getone(r'[0-9a-fA-F]{24}')
        key = item.key
        data = item.data
        if key == KeyEnum.registration or key == KeyEnum.new_login:  # Отправка Email
            try:
                Email_send().send_email(test_email, key.value, f'Test email. {key.value} was entered')
            except Exception:
                return{"message": "issue with SMTP_server"}
            print('email')

            # Обработка ключа registration
            if key == KeyEnum.registration:

                return {"status": 201, "sucsess": True}
            else:

                return {"status": 200, "response": 'new login'}

        # Обработка ключа message
        if key == KeyEnum.new_message:
            output = await gather(do_find({"user_id": ObjectId(user_id)}))
            output = output[0]

            if len(output) != 0:

                nosql = {"$push":
                            {"notifications":
                                {"target_id":
                                    ObjectId(target_id),
                                 "timestamp": time.time(),
                                 "key": key.value,
                                 "is_new": True,
                                 "data": data}}}

                await update({"user_id": ObjectId(user_id)}, nosql)

            else:

                nosql = {"user_id":
                            ObjectId(user_id),
                         "notifications":
                             [{'target_id':
                                   ObjectId(target_id),
                               "timestamp": time.time(),
                               "key": key.value,
                               "is_new": True,
                               "data": data}]}
                await insert(nosql)

            return {"status": 200,
                    "response": 'message accepted'}

        # Обработка ключа post
        elif key == KeyEnum.new_post:
            output = await gather(do_find({"user_id": ObjectId(user_id)}))
            output = output[0]

            if len(output) != 0:
                nosql = {"$push":
                            {"notifications":
                                {"target_id":
                                    ObjectId(target_id),
                                 "timestamp": time.time(),
                                 "key": key.value,
                                 "is_new": True,
                                 "data": data}}}

                await update({"user_id": ObjectId(user_id)}, nosql)

            else:
                nosql = {"user_id":
                            ObjectId(user_id),
                         "notifications":
                             [{'target_id':
                                   ObjectId(target_id),
                               "timestamp": time.time(),
                               "key": key.value,
                               "is_new": True,
                               "data": data}]}

                await insert(nosql)

            return {"status": 200, "response": 'post accepted'}


@app.get("/list")
async def list_com(user_id, skip: int, limit: int):

    if skip < 0:
        skip = 0
    if limit < 1:
        limit = 1

    result = await gather(do_find({"user_id": ObjectId(user_id)}))
    if len(result[0]) == 0:
        return {'message': "there is no such user in DB"}
    else:
        result = result[0][0]["notifications"][skip: skip+limit]
        i = 0
        for item in result:
            if item["is_new"]:
                i = i+1
        return {"success": "True",
                "data":
                    {"elements": len(result),
                        "new": i,
                        "request":
                            {"user_id": user_id,
                                "skip": 0,
                                "limit": 10}},
                    "list": result}


@app.post("/read")
async def read_com(query: List[ReadCom]):
    for item in query:  # Парсим POST запрос
        user_id = item.user_id
        target_id = item.notification_id
        result = await gather(do_find({"user_id": ObjectId(user_id)}))
        result = result[0]
        if len(result) == 0:
            return{"message": "no such notification in DB"}
        else:
            for i in result:
                output_notifications = i["notifications"]
                for j, tar in enumerate(output_notifications):
                    if tar["target_id"] == ObjectId(target_id):
                        output_notifications[j]["is_new"] = False
                output = {"notifications": output_notifications}
                await replace_one({"notifications": output_notifications}, output)

    return 1


if __name__ == '__main__':
    # asyncio.run(handler(doc))  # раскоментировать для первичного заполнения бд
    uvicorn.run("main:app", host='0.0.0.0', port=port, reload=False, workers=3)
