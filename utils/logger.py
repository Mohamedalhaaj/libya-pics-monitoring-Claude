from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(log_file: str | Path = "logs/scraper.log", verbose: bool = False) -> None:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
