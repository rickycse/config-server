import os
from typing import Union

from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder

load_dotenv()

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

@app.get("/")
def health():
    return { "Healthy": 200 }

@app.get('/3d-printing-ug')
def printing_ug():
    collection = db["printing-guide"]
    filter = {"slug": "3d-printing-ug"}
    result = collection.find_one(filter)

    del result["_id"]
    del result["slug"]

    return jsonable_encoder(result)