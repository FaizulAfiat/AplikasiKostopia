# Kostopia - FastAPI Framework Setup

FastAPI backend setup for Kostopia with modular clean architecture, environment configuration, and automatic interactive API documentation.

## Project Structure

```text
kostopia/
├── .env                  # Local environment configuration
├── .env.example          # Template environment configuration
├── .gitignore            # Git ignored files & directories
├── requirements.txt      # Python dependencies
├── README.md             # Documentation
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entrypoint & middleware
│   ├── core/             # Application config and settings
│   │   ├── __init__.py
│   │   └── config.py
│   ├── api/              # API routes & versions
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py
│   ├── models/           # Database / ORM models
│   ├── schemas/          # Pydantic data validation schemas
│   └── services/        # Business logic layer
└── tests/
    ├── __init__.py
    └── test_main.py      # Automated tests with pytest
```

## Getting Started

### 1. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.\.venv\Scripts\activate.bat
```

### 2. Install Dependencies (Already installed if setup script ran)

```powershell
pip install -r requirements.txt
```

### 3. Run Development Server

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Or using python module:
```powershell
python -m uvicorn app.main:app --reload
```

The server will be available at:
- API Root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger UI Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc Docs: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health Check: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### 4. Run Tests

```powershell
pytest
```
