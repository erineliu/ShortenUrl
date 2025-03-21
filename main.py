from fastapi import Depends,FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse,HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import hashlib
import re
import os
from datetime import datetime, timedelta
import json
import validators
import redis.asyncio as redis
from contextlib import asynccontextmanager
import uvicorn



async def lifespan(app: FastAPI):
    redis_connection = redis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    yield

app = FastAPI(lifespan=lifespan)
dataStore ={}


# >curl -X POST -H "Content-Type: application/json" -d "{\"original_url\": \"invalid-urere\"}" http://localhost:8000/api/createShortUrl

@app.get("/api/getShortUrlList")
def getShortUrl(request: Request):
    return JSONResponse(content=json.dumps(dataStore))



@app.post("/api/createShortUrl",dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def createShortUrl(request: Request):
    #print(request.headers['content-length'])
    data =  await request.json()
    origUrl = data['original_url']


    if len(origUrl) > 2048:
        raise HTTPException(
            status_code=400, 
            detail="The URL length exceeds 2048 characters."
        )

    if not validators.url(origUrl):
         raise HTTPException(
            status_code=400, 
            detail="The URL format error"
        )

    
    shortName = str(hashlib.md5(origUrl.encode()).hexdigest()[:4])
    shrotUrl = "http://localhost:8000/shortUrl/" + shortName
    createTime = datetime.now() 
    expireTime = createTime + timedelta(days=30)  

    dataStore[shortName] = {
        "expiration_date": expireTime.isoformat(),
        "original_url": origUrl
    }


    return JSONResponse(content={
        "short_url": shrotUrl,
        "expiration_date": expireTime.isoformat(),
        "success": True
    })



@app.get("/shortUrl/{shortId}")
async def redirectShortUrl(shortId: str):
    curUrl = dataStore[shortId]

    if not curUrl:
        raise HTTPException(status_code=404, detail="Short URL not found")

    if datetime.now() > datetime.fromisoformat(curUrl['expiration_date']):
        raise HTTPException(status_code=410, detail="Short URL expired")


    return RedirectResponse(url=curUrl['original_url'])



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
