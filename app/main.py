import os
import time
import random
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Global state for Chaos Mode
start_time = time.time()
chaos_config = {"mode": "recover", "duration": 0, "rate": 0.0}

class ChaosRequest(BaseModel):
    mode: str
    duration: int = 0
    rate: float = 0.0

@app.middleware("http")
async def apply_chaos_and_headers(request: Request, call_next):
    mode = os.getenv("MODE", "stable")
    
    # 1. Handle Chaos Logic (Only if in Canary mode)
    if mode == "canary":
        if chaos_config["mode"] == "slow":
            time.sleep(chaos_config["duration"])
        elif chaos_config["mode"] == "error":
            if random.random() < chaos_config["rate"]:
                return Response(content="Chaos Error", status_code=500)

    # 2. Process Request
    response = await call_next(request)

    # 3. Add Canary Header
    if mode == "canary":
        response.headers["X-Mode"] = "canary"
    
    return response

@app.get("/")
async def root():
    return {
        "message": "Welcome to SwiftDeploy API",
        "mode": os.getenv("MODE", "stable"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/healthz")
async def healthz():
    uptime = time.time() - start_time
    return {
        "status": "healthy",
        "uptime_seconds": int(uptime)
    }

@app.post("/chaos")
async def set_chaos(config: ChaosRequest):
    # Requirement: Only activate if in Canary mode
    if os.getenv("MODE") != "canary":
        raise HTTPException(status_code=403, detail="Chaos only available in canary mode")
    
    global chaos_config
    chaos_config = {"mode": config.mode, "duration": config.duration, "rate": config.rate}
    return {"message": f"Chaos mode set to {config.mode}"}

if __name__ == "__main__":
    import uvicorn
    # Use APP_PORT env var injected by swiftdeploy CLI
    port = int(os.getenv("APP_PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
