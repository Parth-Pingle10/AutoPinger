from fastapi import FastAPI
import httpx
import asyncio

app = FastAPI()

active_task = {}

async def ping_website(url:str):
    async with httpx.AsyncClient(timeout=15) as client:
        while True:
            try:
                res = await client.get(url)
                print(f"{url} -> {res.status_code}")
            except asyncio.CancelledError:
                print(f"Stopped pinging {url}")
                break
            except Exception as e:
                print(f"{url} -> {e}")
                
            await asyncio.sleep(500)
            

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/start/{url:path}")
async def start(url:str):
    if not url.startswith("http"):
        url = "https://"+url
    
    if url in active_task:
        return {"message": f"Already running {url}"}    
    
    task = asyncio.create_task(ping_website(url))
    
    active_task[url] = task
    
    return{"message":f"Started pinging {url}"}


@app.get("/stop/{url:path}")
async def stop(url:str):
    if not url.startswith("http"):
        url = "https://"+url
    
    if url not in active_task:
        return {"message": f"{url} is not running"}
        
    task = active_task.get(url)
    
    if task:
        task.cancel()
        del active_task[url]
        
    return {"message":f"Stopped pinging {url}"}