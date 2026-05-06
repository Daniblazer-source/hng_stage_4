import os
import time
import random
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

# --- Requirement 1: Instrumentation (/metrics) ---

# Throughput & Errors: http_requests_total
REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP Requests',
    ['method', 'path', 'status_code']
)

# Latency: http_request_duration_seconds (Standard Buckets for P99)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'HTTP request latency',
    ['method', 'path'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 1.0, 2.0, 5.0]
)

# State: Uptime, Mode (0=stable, 1=canary), and Chaos (0=none, 1=slow, 2=error)
APP_UPTIME = Gauge('app_uptime_seconds', 'Seconds since app start')
APP_MODE = Gauge('app_mode', '0=stable, 1=canary')
CHAOS_ACTIVE = Gauge('chaos_active', '0=none, 1=slow, 2=error')

# Global state setup
START_TIME = time.time()
chaos_config = {"mode": "recover", "duration": 0, "rate": 0.0}

class ChaosRequest(BaseModel):
    mode: str
    duration: int = 0
    rate: float = 0.0

@app.middleware("http")
async def monitor_and_chaos(request: Request, call_next):
    mode = os.getenv("MODE", "stable")
    path = request.url.path
    method = request.method

    # 1. Update State Gauges on every request
    APP_UPTIME.set(time.time() - START_TIME)
    APP_MODE.set(1 if mode == "canary" else 0)

    chaos_val = 0
    if chaos_config["mode"] == "slow": chaos_val = 1
    elif chaos_config["mode"] == "error": chaos_val = 2
    CHAOS_ACTIVE.set(chaos_val)

    # 2. Apply Chaos Logic (Requirement #3C)
    if mode == "canary":
        if chaos_config["mode"] == "slow":
            # Simulate high latency
            time.sleep(chaos_config["duration"])
        elif chaos_config["mode"] == "error":
            # Simulate failure rate
            if random.random() < chaos_config["rate"]:
                REQUEST_COUNT.labels(method=method, path=path, status_code=500).inc()
                return Response(content="Chaos Error", status_code=500)

    # 3. Time the request for Latency
    start_req_time = time.perf_counter()
    response = await call_next(request)
    latency = time.perf_counter() - start_req_time

    # 4. Record Performance Metrics
    REQUEST_COUNT.labels(method=method, path=path, status_code=response.status_code).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(latency)

    if mode == "canary":
        response.headers["X-Mode"] = "canary"

    return response

@app.get("/metrics")
async def metrics():
    """Requirement: Expose metrics in Prometheus text format"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {
        "message": "Welcome to SwiftDeploy API",
        "mode": os.getenv("MODE", "stable"),
        "version": os.getenv("APP_VERSION", "1.0.0")
    }

@app.get("/healthz")
async def health():
    return {"status": "healthy"}

@app.post("/chaos")
async def set_chaos(config: ChaosRequest):
    """Control endpoint for injecting failures during testing"""
    if os.getenv("MODE") != "canary":
        raise HTTPException(status_code=403, detail="Chaos only available in canary mode")
    global chaos_config
    chaos_config = {"mode": config.mode, "duration": config.duration, "rate": config.rate}
    return {"message": f"Chaos mode set to {config.mode}"}

if __name__ == "__main__":
    import uvicorn
    # Use environment variables for dynamic configuration
    port = int(os.getenv("APP_PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
