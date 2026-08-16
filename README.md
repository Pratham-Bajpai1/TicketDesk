# TicketDesk - Production-Grade IT Support Ticket Tracking System

TicketDesk is a production-grade, container-ready IT support ticket management backend API and Single Page Application (SPA) built using **Python 3.10+**, **FastAPI**, **SQLAlchemy**, **Alembic**, and **Boto3 (AWS S3)**.

Designed specifically for enterprise cloud deployments on **AWS ECS Fargate**, **AWS RDS (PostgreSQL)**, **AWS S3**, and **AWS Application Load Balancer (ALB)**.

---

## Technical Stack & Architecture

- **Backend Framework**: FastAPI running on Uvicorn.
- **ORM & Database**: SQLAlchemy (Sync/Async compatible) with PostgreSQL (`psycopg2-binary`) & local SQLite fallback.
- **Database Migrations**: Complete setup for Alembic DB schema versioning.
- **Object Storage**: AWS S3 Direct Browser Uploads via `boto3` generated Pre-signed URLs (`PUT` method).
- **Configuration**: Pydantic v2 `BaseSettings` (`pydantic-settings`) dynamically loading environment parameters.
- **Frontend SPA**: Vanilla HTML5/CSS3 (Glassmorphism design system) & JavaScript embedded and CloudFront-ready.

---

## Directory Structure

```text
TicketDesk Application/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, ALB health check & SPA mount
│   ├── config.py            # Pydantic BaseSettings loading env vars
│   ├── db.py                # Database engine, sessionmaker & get_db dependency
│   ├── models.py            # SQLAlchemy entities (Tickets, Comments, Attachments)
│   ├── schemas.py           # Pydantic v2 request/response validation schemas
│   ├── routers/             # API domain endpoints
│   │   ├── __init__.py
│   │   ├── tickets.py       # CRUD & Filtering for tickets
│   │   ├── comments.py      # Threaded ticket discussion comments
│   │   ├── attachments.py   # S3 Pre-signed URL generation & attachment metadata
│   │   └── dashboard.py     # Aggregated ticket analytics & status metrics
│   └── services/            # AWS integration services
│       ├── __init__.py
│       └── s3.py            # Boto3 S3 Pre-signed PUT URL helper
├── frontend/
│   └── index.html           # Embedded single-page web UI
├── alembic/                 # Database migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
├── alembic.ini              # Alembic configuration
├── requirements.txt         # Production dependencies
├── .env.example             # Template environment configuration
└── README.md                # Documentation
```

---

## Local Setup & Quick Start

### 1. Prerequisites
- Python 3.10+
- PostgreSQL (Optional for local development; SQLite works out of the box if no DB credentials provided).

### 2. Installation & Virtual Environment

```bash
# Clone or navigate to the project directory
cd "TicketDesk Application"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the sample environment file:

```bash
cp .env.example .env
```

Key environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DB_HOST` | PostgreSQL Host address | `localhost` |
| `DB_PORT` | Database Port | `5432` |
| `DB_NAME` | Database Name | `ticketdesk` |
| `DB_USER` | Database User | `postgres` |
| `DB_PASSWORD` | Database Password | `postgres` |
| `DATABASE_URL` | Direct connection string override | *(Optional)* |
| `AWS_REGION` | AWS S3 Bucket Region | `us-east-1` |
| `AWS_S3_BUCKET_NAME` | S3 Bucket Name for Attachments | `my-ticketdesk-attachments` |
| `AWS_ACCESS_KEY_ID` | AWS Access Key | *(Optional in dev)* |
| `AWS_SECRET_ACCESS_KEY`| AWS Secret Access Key | *(Optional in dev)* |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma separated) | `*` |

### 4. Database Migrations (Alembic)

To apply database schema migrations:

```bash
alembic upgrade head
```

*(Note: On server startup, `Base.metadata.create_all()` will also automatically verify and create missing tables if needed.)*

### 5. Running the Application Server

Start Uvicorn server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access points:
- **Web SPA Interface**: `http://localhost:8000/`
- **Swagger Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc API Spec**: `http://localhost:8000/redoc`
- **Health Check Probe**: `http://localhost:8000/health`

---

## AWS Deployment Architecture Guide

### 1. Application Load Balancer (ALB) Health Check
Configure the Target Group health check:
- **Path**: `/health`
- **HTTP Code**: `200`
- The endpoint performs a live `SELECT 1` query to RDS PostgreSQL. If DB is unavailable, returns HTTP `500`.

### 2. AWS S3 CORS Configuration
For direct browser-to-S3 uploads via Pre-signed URLs, enable CORS on your S3 bucket:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET", "POST", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"]
  }
]
```

### 3. AWS RDS PostgreSQL Integration
Set environment variables on ECS Task Definition / Secrets Manager:
- `DB_HOST`: RDS Endpoint address
- `DB_USER` & `DB_PASSWORD`: Managed DB credentials
- `DB_NAME`: Database name
