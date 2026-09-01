import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from Graph import run_agent
from db import init_db, save_run, get_run, list_runs, get_metrics

app = FastAPI(title="AI App Builder API")
init_db()

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
AGENT_RUN_COUNT = Counter(
    "agent_runs_total",
    "Total agent generation runs",
    ["status"],
)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    REQUEST_LATENCY.labels(method=request.method, path=request.url.path).observe(duration)
    REQUEST_COUNT.labels(
        method=request.method, path=request.url.path, status_code=response.status_code
    ).inc()
    return response


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    plan: dict
    review_report: list
    status: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def get_metrics_endpoint():
    return get_metrics()


@app.get("/prometheus-metrics")
def prometheus_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        result = run_agent(req.prompt)
    except Exception as e:
        AGENT_RUN_COUNT.labels(status="ERROR").inc()
        raise HTTPException(status_code=502, detail=f"Agent run failed: {e}")
    coder_state = result.get("coder_state")
    plan = coder_state.task_plan.plan.model_dump() if coder_state else {}
    status = result.get("status", "UNKNOWN")
    run_id = save_run(req.prompt, plan, result.get("review_report", []), status)
    AGENT_RUN_COUNT.labels(status=status).inc()
    return GenerateResponse(
        plan=plan,
        review_report=result.get("review_report", []),
        status=status,
    )


@app.get("/runs")
def get_runs():
    return list_runs()


@app.get("/runs/{run_id}")
def get_run_by_id(run_id: int):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run