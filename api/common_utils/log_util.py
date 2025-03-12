import logging
import os
from pathlib import Path



formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
logs_dir = Path("/logs")


def setup_file_logger(name: str, log_file: os.PathLike, level: int = 10):
    log_file_path = logs_dir / log_file
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    if os.path.exists(log_file_path):
        os.remove(log_file_path)

    handler = logging.FileHandler(
        filename=log_file_path, encoding="utf-8", mode="a")
    console_handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    return logger
