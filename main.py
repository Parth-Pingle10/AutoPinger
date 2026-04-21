from fastapi import FastAPI
import httpx
import asyncio
from mongo import client,db,collection
from datetime import datetime,timezone
from contextlib import asynccontextmanager

active_task = {}

async def ping_website(url:str):
    async with httpx.AsyncClient(timeout=15) as client:
        while True:
            try:
                res = await client.get(url)
                status = "active" if res.status_code == 200 else "failed"
                if status == "active":
                    await collection.update_one({"url":url},
                                            {
                                                "$inc" : {"ping_count":1},
                                                "$set" : {"last_ping":datetime.now(timezone.utc),
                                                         "status":status}
                                            })
                
                else:
                    await collection.update_one({"url":url},
                                            {
                                               
                                                "$set" : {"last_ping": datetime.now(timezone.utc),
                                                         "status":status}
                                            })
                print(f"{url} -> {res.status_code}")
                await asyncio.sleep(180)
                
                
            except asyncio.CancelledError:
                await collection.update_one({"url":url},{
                                            "$set":{"last_ping": datetime.now(timezone.utc),"status":"stopped"}
                                            })
                break
            except Exception as e:
                await collection.update_one({"url":url},{
                                            "$set":{"last_ping": datetime.now(timezone.utc),"status":"failed"}
                                            })
                print(f"{url} -> {e}")
                
@asynccontextmanager
async def lifespan(app:FastAPI):
    async for doc in collection.find({"status":"active"}):
        url = doc["url"]
        task = asyncio.create_task(ping_website(url))
        active_task[url]=task
    
    yield
    
    for task in active_task.values():
        task.cancel()
    
    active_task.clear()
    

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/start/{url:path}")
async def start(url:str):
    if not url.startswith("http"):
        url = "https://"+url
        
    existing = await collection.find_one({"url":url})
    
    if existing and existing["status"] == "active" and url in active_task:
        return {"message": f"Already running {url}"}
    
    if url in active_task:
        active_task[url].cancel()
        del active_task[url]
    
    if not existing:
        await collection.insert_one({
            "url":url,
            "ping_count":0,
            "last_ping":None,
            "status":"active",
            "created_at":datetime.now(timezone.utc),
        }) 
    else:
        await collection.update_one({"url":url},{"$set":{"status":"active"}})
    
    task = asyncio.create_task(ping_website(url))
    active_task[url] = task
    
    return{"message":f"Started pinging {url}"}

@app.get("/stats/{url:path}")
async def stats(url:str):
    if not url.startswith("http"):
        url = "https://"+url
        
    doc = await collection.find_one({"url":url})
    
    if not doc:
        return{"message":f"{url} is not running"}
                
    last_ping = str(doc.get("last_ping"))
    created_at = str(doc.get("created_at"))
    
    last_data = last_ping.split(" ")[0]
    created_data = created_at.split(" ")[0]
    
    last_time =  get_ist_time(last_ping)
    created_time =  get_ist_time(created_at)
    
    return{
        "url":url,
        "ping_count":doc.get("ping_count"),
        "last_ping":{
            "date":last_data,
            "time":last_time,
        },
        "status":doc.get("status"),
        "created_at":{
            "date":created_data,
            "time":created_time,
        }
    }
        
        
        

def get_ist_time(time: str):
    if not time or time == "None":
        return "Never"

    # 🔥 handle both formats (T or space)
    if "T" in time:
        time_part = time.split("T")[1]
    else:
        time_part = time.split(" ")[1]

    time_part = time_part.split("+")[0]

    hour = int(time_part.split(":")[0])
    minute = int(time_part.split(":")[1])
    second = int(time_part.split(":")[2].split(".")[0])

    hour += 5
    minute += 30

    if minute >= 60:
        hour += minute // 60
        minute = minute % 60

    if hour >= 12:
        hour = hour % 12

    return f"{hour:02d}:{minute:02d}:{second:02d}"
    

@app.get("/stop/{url:path}")
async def stop(url:str):
    if not url.startswith("http"):
        url = "https://"+url
    
    existing = await collection.find_one({"url":url})

    if not existing or existing.get("status") != "active":
        return {"message": f"{url} is not running"}
    
    task = active_task.get(url)
    if task:
        task.cancel()
        del active_task[url]
        
    await collection.update_one(
    {"url": url},
    {"$set": {"status": "stopped"}}
    )
        
    return {"message":f"Stopped pinging {url}"}
