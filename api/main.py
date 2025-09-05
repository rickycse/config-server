import os
from typing import Union

from fastapi import Depends, FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder

from auth import verify_internal_secret

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

@app.get('/content/static', dependencies=[Depends(verify_internal_secret)])
def static_content():
    return get_content("static")

@app.get('/content/problems', dependencies=[Depends(verify_internal_secret)])
def problems():
    return get_content("problems")

@app.get('/content/safety', dependencies=[Depends(verify_internal_secret)])
def safety():
    return get_content("safety")

@app.get('/content/filaments', dependencies=[Depends(verify_internal_secret)])
def filaments():
    return get_content("filaments")

@app.get('/content/printers', dependencies=[Depends(verify_internal_secret)])
def filament():
    return get_content("printers")

@app.get('/content/concerns', dependencies=[Depends(verify_internal_secret)])
def concerns():
    return get_content("concerns")