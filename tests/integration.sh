#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

echo "Submitting job to ${API_BASE_URL}/jobs"
timeout 15s curl -fsS -X POST "${API_BASE_URL}/jobs" > response.json
cat response.json

JOB_ID=$(python3 -c "import json; print(json.load(open('response.json'))['job_id'])")
echo "Polling job: ${JOB_ID}"

timeout 90s bash -c '
  set -euo pipefail
  while true; do
    STATUS=$(curl -fsS "'"${API_BASE_URL}"'/jobs/'"${JOB_ID}"'" | python3 -c "import sys, json; print(json.load(sys.stdin).get('"'"'status'"'"', '"'"'unknown'"'"'))")
    echo "Current status: ${STATUS}"
    if [ "${STATUS}" = "completed" ]; then
      exit 0
    fi
    sleep 3
  done
'

echo "Integration check passed"
