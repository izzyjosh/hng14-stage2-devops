import os
import sys
from pathlib import Path
from uuid import UUID
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

# Ensure environment variables exist before importing the app module.
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")

# Allow importing api/main.py as module "main" when tests run from repo root.
sys.path.append(str(Path(__file__).resolve().parents[1]))
import main  # noqa: E402

client = TestClient(main.app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job_pushes_to_queue_and_sets_status(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr(main, "r", mock_redis)

    fixed_uuid = UUID("12345678-1234-5678-1234-567812345678")
    monkeypatch.setattr(main.uuid, "uuid4", lambda: fixed_uuid)

    response = client.post("/jobs")

    assert response.status_code == 200
    assert response.json() == {"job_id": str(fixed_uuid)}
    mock_redis.lpush.assert_called_once_with("job", str(fixed_uuid))
    mock_redis.hset.assert_called_once_with(
        f"job:{fixed_uuid}", "status", "queued"
    )


def test_get_job_returns_status_when_found(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.hget.return_value = b"completed"
    monkeypatch.setattr(main, "r", mock_redis)

    job_id = "job-123"
    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json() == {"job_id": job_id, "status": "completed"}
    mock_redis.hget.assert_called_once_with(f"job:{job_id}", "status")


def test_get_job_returns_not_found_when_missing(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.hget.return_value = None
    monkeypatch.setattr(main, "r", mock_redis)

    job_id = "missing-job"
    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json() == {"error": "not found"}
    mock_redis.hget.assert_called_once_with(f"job:{job_id}", "status")
