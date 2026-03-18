#!/bin/bash
set -e
echo "Starting Decentralized Finance Risk Assessment Tool..."
uvicorn app:app --host 0.0.0.0 --port 9106 --workers 1
