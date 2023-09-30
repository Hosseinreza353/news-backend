#!/bin/sh
service cron start
cd /usr/app && python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
