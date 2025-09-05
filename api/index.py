from collections import defaultdict, deque
import os
import time
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, Request
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

"""
I'm using a single process rate limit here because Render only allows 1 instance of a webservice when hosted. 
I plan to switch to Redis once I get multi-instance hosting.
"""
WINDOW = int(os.getenv("RATE_WINDOW"))
LIMIT = int(os.getenv("RATE_LIMIT"))

buckets: dict[str, deque[float]] = defaultdict(deque)
def _key_from_request(req: Request) -> str:
    return req.client.host or "unknown"

@app.middleware("http")
async def simple_rate_limit(request: Request, call_next):
    key = _key_from_request(request)
    now = time.time()

    q = buckets[key]
    while q and now - q[0] > WINDOW:
        q.popleft()

    if len(q) >= LIMIT:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    q.append(now)
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(max(0, LIMIT - len(q)))
    response.headers["X-RateLimit-Reset"] = str(int(now + WINDOW))
    return response

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

@app.get("/printing-ug/{slug}", dependencies=[Depends(verify_internal_secret)])
def get_content_route(slug: str):
    if slug not in ALLOWED_SLUGS:
        raise HTTPException(status_code=404, detail="Not found")
    
    collection = db["printing-guide"]
    return get_content(slug, collection)