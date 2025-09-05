import os
from typing import Union

from fastapi import Depends, FastAPI, HTTPException
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

def get_content(slug, collection):
    filter = {
        "slug": slug
    }
    result = collection.find_one(filter)

    del result["_id"]
    del result["slug"]

    return jsonable_encoder(result)

ALLOWED_SLUGS = {"static", "problems", "safety", "filaments", "printers", "concerns"}

@app.get("/printer-ug/{slug}", dependencies=[Depends(verify_internal_secret)])
def get_content_route(slug: str):
    if slug not in ALLOWED_SLUGS:
        raise HTTPException(status_code=404, detail="Not found")
    
    collection = db["printing-guide"]
    return get_content(slug, collection)