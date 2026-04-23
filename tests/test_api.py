import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient


os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")

sys.path.append(str(Path(__file__).resolve().parents[1] / "api"))
from api.main import main  # noqa: E402


client = TestClient(main.app)


def test_create_job_returns_job_id_and_queues_job(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr(main, "r", mock_redis)

    response = client.post("/jobs")

    assert response.status_code == 200
    assert "job_id" in response.json()
    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()


def test_get_job_returns_completed_status_when_found(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.hget.return_value = b"completed"
    monkeypatch.setattr(main, "r", mock_redis)

    response = client.get("/jobs/sample-id")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_get_job_returns_not_found_when_missing(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.hget.return_value = None
    monkeypatch.setattr(main, "r", mock_redis)

    response = client.get("/jobs/missing-id")

    assert response.status_code == 200
    assert response.json() == {"error": "not found"}
