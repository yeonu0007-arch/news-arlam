#!/bin/bash
cd "$(dirname "$0")/scraper-lambda"
~/.local/bin/poetry run python src/local_server.py
