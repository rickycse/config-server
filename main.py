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

def get_content(slug):
    collection = db["printing-guide"]
    filter = {
        "slug": slug
    }
    result = collection.find_one(filter)

    del result["_id"]
    del result["slug"]

    return jsonable_encoder(result)

@app.get('/content/static')
def static_content():
    return get_content("static")

@app.get('/content/problems')
def problems():
    return get_content("problems")

@app.get('/content/safety')
def safety():
    return get_content("safety")

@app.get('/content/filaments')
def filaments():
    return get_content("filaments")

@app.get('/content/printers')
def filament():
    return get_content("printers")