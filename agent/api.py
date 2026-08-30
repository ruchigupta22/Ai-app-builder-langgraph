from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Graph import run_agent
from db import init_db, save_run, get_run, list_runs

app = FastAPI(title="AI App Builder API")
init_db()


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    plan: dict
    review_report: list
    status: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        result = run_agent(req.prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Agent run failed: {e}")

    coder_state = result.get("coder_state")
    plan = coder_state.task_plan.plan.model_dump() if coder_state else {}
    run_id = save_run(req.prompt, plan, result.get("review_report", []), result.get("status", "UNKNOWN"))
    return GenerateResponse(
        plan=plan,
        review_report=result.get("review_report", []),
        status=result.get("status", "UNKNOWN"),
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