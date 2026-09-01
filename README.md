# AI App Builder — Multi-Agent System (LangGraph)

A multi-agent AI system that transforms a natural language prompt into a working web application. It orchestrates four LangGraph agents — Planner, Architect, Coder, and Reviewer — and is wrapped in a production-style FastAPI service with structured logging, retry logic, SQLite persistence, Docker containerization, CI/CD, Kubernetes deployment with observability, scheduled workflow orchestration, and infrastructure-as-code.

## Architecture

User Prompt
↓
Planner Agent (generates a structured Plan)
↓
Architect Agent (breaks Plan into ImplementationTasks)
↓
Coder Agent (loops through tasks, writes files via tool calls)
↓
Reviewer Agent (validates every file exists and parses correctly)
↓
FastAPI Response (persisted to SQLite)

- **Planner** converts the user's prompt into a structured `Plan` (name, description, tech stack, features, files) using an LLM with Pydantic-enforced structured output.
- **Architect** expands the `Plan` into a `TaskPlan` — a list of file-level implementation tasks with dependencies and integration details.
- **Coder** is a ReAct agent with filesystem tools (`read_file`, `write_file`, `list_files`) that executes each task sequentially, reading existing file content before writing to maintain consistency.
- **Reviewer** re-reads every file from disk after the Coder finishes and validates it — checking for non-empty content and, for `.py` files, valid syntax via Python's `ast` module.

## Features

- Multi-agent orchestration using LangGraph's `StateGraph`, with conditional routing between the Coder loop and Reviewer
- Structured outputs enforced via Pydantic at every agent boundary
- Path-scoped file operations — a `safe_path_for_project()` guard prevents path traversal outside the generated project directory
- Retry logic with exponential backoff on LLM calls (Planner, Architect, and Coder), handling transient failures like malformed tool calls and rate limits
- Structured logging (Python's `logging` module) instead of print statements
- SQLite persistence layer storing every run's prompt, plan, review report, and status
- Dockerized and deployable as a standalone container
- GitHub Actions CI pipeline running the full test suite on every push
- Deployed on Kubernetes (AKS) with multi-replica scheduling, health probes, and self-healing
- Prometheus/Grafana observability and a scheduled Airflow reprocessing workflow

## Tech Stack

Python · LangGraph · LangChain · Groq · FastAPI · Pydantic · SQLite · pytest · Docker · GitHub Actions · Kubernetes (AKS) · Prometheus · Grafana · Helm · Apache Airflow · Terraform · Azure

## Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- A Groq API key ([console.groq.com](https://console.groq.com))

### Local Setup
```bash
git clone https://github.com/ruchigupta22/Ai-app-builder-langgraph.git
cd Ai-app-builder-langgraph
uv sync
```

Create a `.env` file inside `agent/`:

```
GROQ_API_KEY=your_key_here
```

### Run Locally
```bash
cd agent
uv run uvicorn api:app --reload
```
Visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Run with Docker
```bash
docker build -t ai-app-builder .
docker run -p 8000:8000 --env-file .env ai-app-builder
```

## API Endpoints

| Method | Path                 | Description                                  |
|--------|----------------------|-----------------------------------------------|
| GET    | `/health`            | Health check                                  |
| POST   | `/generate`          | Runs the full agent pipeline for a prompt     |
| GET    | `/runs`              | Lists recent runs                             |
| GET    | `/runs/{id}`         | Fetches full details of a specific run        |
| GET    | `/metrics`           | JSON summary of run counts by status          |
| GET    | `/prometheus-metrics`| Prometheus-format metrics (request counts, latency, agent run outcomes) |

## Testing

```bash
cd agent
uv run pytest -v
```

7 tests covering the AST-based file validator (`reviewer.py`) and the path-traversal guard (`tools.py`) — both isolated from the LLM and filesystem, so they run in milliseconds.

## CI/CD

GitHub Actions runs the full test suite on every push to `main` and every pull request. Workflow defined in `.github/workflows/ci.yml`.

## Deployment

Deployed on Azure Kubernetes Service (AKS) — a single-node cluster (`standard_b2s_v2`) running a 2-replica Deployment with liveness/readiness probes, ConfigMap/Secret-based configuration, and a LoadBalancer Service exposing the app publicly. Container images are built via Docker and pushed to Azure Container Registry (ACR), with AKS pulling images directly via an attached ACR identity.

**Self-healing verified**: deleting a running pod resulted in a replacement pod reaching `Running` state in ~2 seconds, with zero request downtime across the deployment's second replica.

Originally deployed on Azure Container Instances (ACI) for simplicity; migrated to AKS to add genuine container-orchestration depth — multi-replica scheduling, health probes, and self-healing that ACI's single-container model doesn't provide.

Infrastructure (resource group, ACR, AKS cluster) is also defined as code in `terraform/main.tf`, imported from the existing manually-provisioned resources via `terraform import` and verified with `terraform plan`.

## Observability

- **Prometheus + Grafana** (installed via Helm's `kube-prometheus-stack`) monitor the deployed service. A custom `/prometheus-metrics` endpoint (using `prometheus-client`) exposes request counts, request latency, and agent-run outcomes, scraped every 15 seconds via a Kubernetes `ServiceMonitor`.
- A Grafana dashboard visualizes request rate by endpoint from real production traffic.
- **Scheduled reprocessing via Apache Airflow**: a DAG (`airflow/health_check_reprocess_dag.py`) runs every 15 minutes, checking the API's `/runs` endpoint for failed generations and automatically retrying them via `/generate`. Confirmed running reliably in production: 4 consecutive scheduled runs, 100% success rate, ~15-27 second execution time per run.

## Known Limitations

- Groq's free tier enforces both per-minute and per-day token limits; complex prompts with many implementation steps can hit these limits mid-run, resulting in partial file generation (correctly surfaced by the Reviewer as `MISSING` rather than silently failing)
- No authentication currently on the API — anyone with the URL can call `/generate`
- SQLite is appropriate for this project's scale but would need to move to Postgres for concurrent multi-user production use
- The Coder agent occasionally splits a single file across multiple implementation steps, which increases LLM call volume and rate-limit exposure
- The AKS cluster runs a single node — self-healing is demonstrated at the pod level (multi-replica), not node-level failover
- Grafana and Airflow are configured for demonstration purposes (`SequentialExecutor`, no persistent volume tuning) rather than production-grade HA setups
- Terraform config was written for the existing manually-provisioned resources; `terraform plan` shows a replace-diff due to incomplete resource attribute coverage — deliberately not applied to avoid destroying the live cluster, a reflection of understanding Terraform's state model rather than a finished IaC migration

## Learning Outcomes

Building this project involved hands-on work with: multi-agent orchestration and state management in LangGraph, structured output validation with Pydantic, retry/backoff patterns for LLM reliability, REST API design with FastAPI, SQLite schema design, Docker containerization, debugging CI/CD dependency drift between local and remote environments, end-to-end cloud deployment on Azure (including resource provisioning, container registries, and container instances), Kubernetes deployment and operations (Deployments, Services, ConfigMaps, Secrets, liveness/readiness probes, rolling updates), observability tooling (Prometheus, Grafana, Helm chart installation and configuration), workflow orchestration with Apache Airflow (DAG design, task dependencies, XCom, scheduled execution), and infrastructure-as-code fundamentals with Terraform (resource import, state management, plan/apply safety).

