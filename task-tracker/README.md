# Task Tracker API

A minimal learning-project REST API built with **FastAPI** and **Pydantic**, using a local JSON file for data persistence (see ADR-001). This project focuses on learning REST API development, request validation, and application structure — not database technologies.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- Local JSON file (`tasks.json`) for persistence (added in a later step)
- HTML/CSS/JavaScript frontend using the Fetch API (added in a later step)

## Current Scope

This skeleton currently includes:
- Basic FastAPI application setup
- A `GET /health` endpoint for verifying the service is running

CRUD endpoints, storage logic, authentication, and the frontend are intentionally **not** included yet — they will be added in later steps.

## Prerequisites

- Python 3.10 or higher
- `pip`

## Setup Instructions

1. Clone or download this project, then move into the project folder:
```bash
   cd task-tracker
```

2. Create a virtual environment:
```bash
   python -m venv venv
```

3. Activate the virtual environment:

   - **Linux/macOS:**
```bash
     source venv/bin/activate
```
   - **Windows (PowerShell):**
```powershell
     venv\Scripts\Activate.ps1
```

4. Install dependencies:
```bash
   pip install -r requirements.txt
```

5. Copy the example environment file and adjust if needed:
```bash
   cp .env.example .env
```
   (On Windows PowerShell: `Copy-Item .env.example .env`)

## Running the Server

Start the development server with auto-reload enabled:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## Testing the Health Endpoint

Use `curl` to verify the server is running:

```bash
curl http://127.0.0.1:8000/health
```

Expected response shape:

```json
{
  "status": "ok",
  "timestamp": "2026-07-05T12:34:56.789012+00:00"
}
```

## API Documentation (Swagger UI)

Once the server is running, open your browser to:
http://127.0.0.1:8000/docs

This provides interactive, auto-generated API documentation courtesy of FastAPI.

## Project Status

This is an early-stage skeleton (Module 1). Future modules will add task CRUD endpoints, JSON file-based storage logic, and a simple frontend.