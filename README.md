# AI App Builder — Multi-Agent System (LangGraph)

A multi-agent AI system that transforms a natural language prompt into a working web application. It orchestrates four LangGraph agents — Planner, Architect, Coder, and Reviewer — and is wrapped in a production-style FastAPI service with structured logging, retry logic, SQLite persistence, Docker containerization, CI/CD, and a live Azure deployment.

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
- Live deployment on Azure Container Instances

## Tech Stack

Python · LangGraph · LangChain · Groq · FastAPI · Pydantic · SQLite · pytest · Docker · GitHub Actions · Azure Container Instances

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

GROQ_API_KEY=your_key_here


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

| Method | Path            | Description                                  |
|--------|-----------------|-----------------------------------------------|
| GET    | `/health`       | Health check                                  |
| POST   | `/generate`     | Runs the full agent pipeline for a prompt     |
| GET    | `/runs`         | Lists recent runs                             |
| GET    | `/runs/{id}`    | Fetches full details of a specific run        |

## Testing

```bash
cd agent
uv run pytest -v
```

7 tests covering the AST-based file validator (`reviewer.py`) and the path-traversal guard (`tools.py`) — both isolated from the LLM and filesystem, so they run in milliseconds.

## CI/CD

GitHub Actions runs the full test suite on every push to `main` and every pull request. Workflow defined in `.github/workflows/ci.yml`.

## Deployment

Containerized with Docker and deployed on Azure Container Instances (ACI) — chosen over AKS/App Service to avoid unnecessary orchestration complexity for a single-container service.

## Known Limitations

- Groq's free tier enforces both per-minute and per-day token limits; complex prompts with many implementation steps can hit these limits mid-run, resulting in partial file generation (correctly surfaced by the Reviewer as `MISSING` rather than silently failing)
- No authentication currently on the API — anyone with the URL can call `/generate`
- SQLite is appropriate for this project's scale but would need to move to Postgres for concurrent multi-user production use
- The Coder agent occasionally splits a single file across multiple implementation steps, which increases LLM call volume and rate-limit exposure

## Learning Outcomes

Building this project involved hands-on work with: multi-agent orchestration and state management in LangGraph, structured output validation with Pydantic, retry/backoff patterns for LLM reliability, REST API design with FastAPI, SQLite schema design, Docker containerization, debugging CI/CD dependency drift between local and remote environments, and end-to-end cloud deployment on Azure (including resource provisioning, container registries, and container instances).

## License

MIT