# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
from contextlib import asynccontextmanager # 1. Import the async context manager
from backend.router import evaluate_routing_plans
from backend.database import init_db, log_batch, get_batch_history

# 2. Define the modern lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs right when the backend boots up
    init_db()
    yield
    # You can put shutdown code here if needed later

# 3. Pass the lifespan handler directly into your FastAPI instance
app = FastAPI(title="RouteIQ REST Endpoint", lifespan=lifespan)

class OptimizationRequest(BaseModel):
    locations: List[Tuple[float, float]]
    scenario: str

@app.post("/api/optimize")
def optimize_batch(payload: OptimizationRequest):
    if not (3 <= len(payload.locations) <= 6):
        raise HTTPException(status_code=400, detail="Provide between 3 and 6 locations.")
    try:
        results = evaluate_routing_plans(payload.locations, scenario=payload.scenario)
        
        b_eta = results["baseline"]["eta"]
        o_eta = results["optimized"]["eta"]
        savings = ((b_eta - o_eta) / b_eta) * 100
        
        log_batch(payload.scenario, len(payload.locations), b_eta, o_eta, round(savings, 2))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
def get_history():
    return get_batch_history()