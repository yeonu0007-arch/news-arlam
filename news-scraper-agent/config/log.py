import logging
from config.env_config import env
from datetime import datetime, timezone, timedelta
from enum import Enum
from rich.console import Console
from rich.json import JSON
from rich.logging import RichHandler
from rich.table import Table
from rich.text import Text
from typing import Any


class ConsoleDataType(Enum):
    TABLE = "TABLE"
    JSON = "JSON"
    TEXT = "TEXT"
    DICT = "DICT"


class NewsScraperAgentLogger(logging.Logger):
    def __init__(self, name: str = "NewsScraperAgent"):
        super().__init__(name)

        self.console = Console()
        self._initialize_logger()

    def _initialize_logger(self):
        # Formatter 설정
        formatter = logging.Formatter(fmt="%(asctime)s - %(name)16s - %(levelname)s - %(message)s")

        # Logger 레벨 설정
        self.setLevel(logging.DEBUG if env.PROFILE != "prod" else logging.INFO)

        # RichHandler 추가 (콘솔 출력용)
        rich_handler = RichHandler(
            rich_tracebacks=True,
            console=self.console,
            log_time_format=lambda dt: Text(
                datetime.fromtimestamp(
                    dt.timestamp(), tz=timezone(timedelta(hours=9))
                ).strftime("%Y-%m-%d %H:%M:%S")
            ),
        )
        rich_handler.setLevel(logging.DEBUG)
        rich_handler.setFormatter(logging.Formatter(fmt="%(name)16s - %(message)s"))
        self.addHandler(rich_handler)

        # FileHandler 추가 (기록용)
        log_file_path = "logs.txt" if env.PROFILE == "local" else "/tmp/logs.txt"
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

    def console_print(self, data_type: ConsoleDataType, data: Any):
        display_text = self._to_console_text(data_type, data)
        self.info(f"{display_text}")

    def _to_console_text(self, data_type: ConsoleDataType, data: Any):
        with self.console.capture() as capture:
            if data_type == ConsoleDataType.TABLE and isinstance(data, Table):
                self.console.print(data)
            elif data_type == ConsoleDataType.JSON:
                self.console.print(JSON.from_data(data))  # JSON 문자열로 표시 (" 포함)
            elif data_type == ConsoleDataType.DICT:
                self.console.print(
                    JSON.from_data(data)
                )  # dict를 JSON 형태로 예쁘게 표시
            elif data_type == ConsoleDataType.TEXT:
                self.console.print(data)
        return Text.from_ansi(capture.get())


if __name__ == "__main__":
    # 로그 테스트 (python -m config.log)
    logger = NewsScraperAgentLogger("NewsScraperAgent")

    # 로그 메시지 테스트
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # console_print 사용 예시
    sample_data = {"key": "value", "another_key": "another_value"}
    logger.console_print(ConsoleDataType.DICT, sample_data)
