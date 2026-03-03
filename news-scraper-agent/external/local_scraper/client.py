import json
import time

import requests

from config.log import NewsScraperAgentLogger


class LocalScraperClient:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.logger = NewsScraperAgentLogger(self.__class__.__name__)

    def invoke(self, logging_name: str = None, **kwargs) -> dict:
        name = logging_name or "Local scraper"
        payload = json.loads(kwargs["Payload"])

        start = time.time()
        self.logger.info(f"Started {name}")

        response = requests.post(self.base_url, json=payload, timeout=120)
        result = response.json()

        if result.get("statusCode") != 200:
            body = json.loads(result.get("body", "{}"))
            raise RuntimeError(f"Scraper 호출 실패: {body.get('message', 'unknown error')}")

        body = json.loads(result["body"])

        end = time.time()
        self.logger.info(f"Finished {name} ({end - start:.2f}s)")

        return body
