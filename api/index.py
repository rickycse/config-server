import os
from functools import lru_cache
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/debug/env")
def debug_env():
    return {
        "has_INTERNAL_API_SECRET": bool(os.getenv("INTERNAL_API_SECRET")),
        "has_MONGO_URI": bool(os.getenv("MONGO_URI")),
        "has_MONGO_DB": bool(os.getenv("MONGO_DB")),
    }

def verify_internal_secret(request: Request):
    secret = os.getenv("INTERNAL_API_SECRET") or ""
    if not secret:
        raise HTTPException(status_code=500, detail="Server missing INTERNAL_API_SECRET")
    if request.headers.get("x-internal-secret") != secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

@lru_cache
def get_db():
    uri = os.getenv("MONGO_URI")
    name = os.getenv("MONGO_DB")
    if not uri or not name:
        raise RuntimeError("MONGO_URI and/or MONGO_DB not set")
    client = MongoClient(uri)
    return client[name]

def fetch_content(slug: str):
    db = get_db()
    doc = db["printing-guide"].find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail=f"{slug!r} not found")
    doc.pop("_id", None)
    doc.pop("slug", None)
    return jsonable_encoder(doc)

@app.get('/content/static',    dependencies=[Depends(verify_internal_secret)])
def static_content():
    return fetch_content("static")

@app.get('/content/problems',  dependencies=[Depends(verify_internal_secret)])
def problems():
    return fetch_content("problems")

@app.get('/content/safety',    dependencies=[Depends(verify_internal_secret)])
def safety():
    return fetch_content("safety")

@app.get('/content/filaments', dependencies=[Depends(verify_internal_secret)])
def filaments():
    return fetch_content("filaments")

@app.get('/content/printers',  dependencies=[Depends(verify_internal_secret)])
def printers():
    return fetch_content("printers")

@app.get('/content/concerns',  dependencies=[Depends(verify_internal_secret)])
def concerns():
    return fetch_content("concerns")
