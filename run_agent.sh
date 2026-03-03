#!/bin/bash
cd "$(dirname "$0")/news-scraper-agent"
~/.local/bin/poetry run python main.py
