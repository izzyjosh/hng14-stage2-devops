# Job Queue Microservices

A distributed job processing system built with FastAPI (API), Node.js (Frontend), Python (Worker), and Redis.

## Architecture

- **API**: FastAPI service that accepts job submissions and returns job status
- **Frontend**: express.js web UI for submitting jobs and monitoring status
- **Worker**: Python background service that processes jobs from the Redis queue
- **Redis**: Message queue and job state storage

## Prerequisites

Before starting, ensure you have the following installed on your machine:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/) (includes Docker Compose v2)
- **Git**: For cloning the repository
- **Python 3.12+** (optional, for local development/testing)
- **Node.js 18+** (optional, for local development/testing)

### Verify Prerequisites

```bash
docker --version
docker compose version
git --version
```

All three should return version numbers. If any are missing, install them before proceeding.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/izzjosh/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Create Environment File

Copy the template and set values (defaults work for local development):

```bash
cp .env.example .env
```

For local development, the defaults in `.env.example` are sufficient. For production, update values as needed.

### 3. Start the Stack

```bash
docker compose up -d --build
```

This command:
- Builds Docker images for api, worker, and frontend from Dockerfiles
- Starts all services: Redis, API, worker, and frontend
- Exposes ports 3000 (frontend) and 8000 (API)

### 4. Verify Services Are Running

Check that all containers are healthy:

```bash
docker compose ps
```

**Expected output:**
```
NAME      IMAGE                    COMMAND                STATUS
redis     redis:7                  "redis-server"         Up (healthy)
api       hng14-stage2-devops-api  "uvicorn main:app..."  Up (healthy)
worker    hng14-stage2-devops-...  "python worker.py"     Up
frontend  hng14-stage2-devops-...  "node app.js"          Up (healthy)
```

### 5. Access the Application

- **Frontend UI**: http://localhost:3000
- **API Health**: http://localhost:8000/health
- **API Docs (Swagger)**: http://localhost:8000/docs

## What a Successful Startup Looks Like

### Health Checks

All services should respond to health endpoints:

```bash
# API health
curl http://localhost:8000/health
# Expected response: {"status": "ok"}

# Frontend health
curl http://localhost:3000/health
# Expected response: {"status": "OK"}
```

### Submit a Job

```bash
curl -X POST http://localhost:8000/jobs
# Expected response: {"job_id": "a1b2c3d4-..."}
```

### Check Job Status

```bash
curl http://localhost:8000/jobs/<job_id>
# Expected responses:
# {"job_id": "<id>", "status": "queued"}
# {"job_id": "<id>", "status": "completed"}
```

### Web UI

1. Open http://localhost:3000 in your browser
2. Click "Submit New Job"
3. A job ID should appear immediately
4. Job status updates from "queued" → "completed" within a few seconds
5. Completed jobs stop updating

## Common Commands

### View Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs api
docker compose logs worker
docker compose logs frontend
docker compose logs redis

# Follow logs in real-time
docker compose logs -f api
```

### Stop Services

```bash
docker compose down
```

This stops and removes all containers but preserves the built images.

### Restart Services

```bash
docker compose restart
```

### Clean Everything (Hard Reset)

```bash
# Stop containers and remove images
docker compose down --rmi all

# Then rebuild and restart
docker compose up -d --build
```

## Environment Variables

All required variables are defined in `.env.example`. Common configurations:

| Variable | Default | Purpose |
|----------|---------|---------|
| `REDIS_IMAGE` | `redis:7` | Redis Docker image |
| `REDIS_HOST` | `redis` | Redis hostname (service name in compose) |
| `REDIS_PORT` | `6379` | Redis port |
| `API_PORT` | `8000` | API port on host machine |
| `API_INTERNAL_PORT` | `8000` | API port inside container |
| `FRONTEND_PORT` | `3000` | Frontend port on host machine |
| `FRONTEND_INTERNAL_PORT` | `3000` | Frontend port inside container |
| `API_URL` | `http://api:8000` | API endpoint URL for frontend |

## Troubleshooting

### Services Won't Start

Check logs for errors:

```bash
docker compose logs
```

Common issues:
- **Port already in use**: Change `API_PORT` or `FRONTEND_PORT` in `.env`
- **Missing environment variables**: Ensure `.env` file exists and is readable
- **Out of disk space**: Run `docker system prune` to clean up unused images

### API Container Crashes

The API requires Redis to be running first. Compose dependency ensures Redis starts first with health checks. If still failing:

```bash
docker compose logs api
```

### Job Not Completing

Check that the worker is running and connected to Redis:

```bash
docker compose logs worker
docker compose logs redis
```

### Cannot Connect to Localhost Ports

On some systems (especially Windows/WSL2), use `127.0.0.1` instead of `localhost`:

```bash
curl http://127.0.0.1:8000/health
```

## Development Workflow

### Running Tests Locally

```bash
# API tests (with mocked Redis)
cd api
pip install -r requirements.txt
pip install pytest pytest-cov
pytest --cov=. --cov-report=html

# Frontend linting
cd frontend
npm ci
npx eslint .
```

### Running Without Docker

To run services locally for development:

```bash
# Terminal 1: Redis
docker run -d -p 6379:6379 redis:7

# Terminal 2: API
cd api
pip install -r requirements.txt
export REDIS_HOST=localhost REDIS_PORT=6379
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Worker
cd worker
pip install -r requirements.txt
export REDIS_HOST=localhost REDIS_PORT=6379
python worker.py

# Terminal 4: Frontend
cd frontend
npm ci
npm start
```

## CI/CD Pipeline

This repository includes a GitHub Actions workflow that runs:
1. **Lint**: Python (flake8), JavaScript (ESLint), Dockerfiles (hadolint)
2. **Test**: API unit tests with mocked Redis
3. **Build**: Docker images for all services
4. **Security**: Trivy vulnerability scans
5. **Integration**: End-to-end test with Docker Compose
6. **Deploy**: Rolling deployment with health checks

See `.github/workflows/ci.yml` for full pipeline configuration.

## API Endpoints

### Create Job
```
POST /jobs
Response: {"job_id": "uuid-string"}
```

### Get Job Status
```
GET /jobs/{job_id}
Response: {"job_id": "uuid-string", "status": "queued|completed"}
         or {"error": "not found"}
```

### Health Check
```
GET /health
Response: {"status": "ok"}
```

## Architecture Decisions

- **Redis**: Lightweight, fast queue for job management
- **FastAPI**: Modern Python framework with automatic Swagger docs
- **Express.js**: Lightweight Node.js framework for frontend
- **Docker Compose**: Simplified local orchestration
- **Health Checks**: Ensures services are ready before processing requests

## Performance

- Job submission: < 10ms
- Job processing: ~2 seconds (includes simulated work)
- Status polling: < 5ms

## Security Considerations

- All services run as non-root users in containers
- Redis is only accessible from within Docker network
- API validates all inputs
- Frontend uses secure headers via Express middleware

For production deployments:
- Use environment variables for sensitive data (API keys, credentials)
- Enable Redis authentication and persistence
- Run behind HTTPS/TLS proxy
- Implement rate limiting and request validation
- Use container registry scanning for vulnerabilities
- Enable audit logging

## Support

For issues or questions:
1. Check logs: `docker compose logs`
2. Verify prerequisites are installed
3. Review Troubleshooting section above
4. Check GitHub Issues in the repository

## License

[Your License Here]
