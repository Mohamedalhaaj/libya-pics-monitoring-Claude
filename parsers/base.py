from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from utils.models import Article


class BaseParser(ABC):
    def __init__(self, source: dict[str, Any], keywords: list[str]) -> None:
        self.source = source
        self.keywords = keywords

    @abstractmethod
    def parse(self, html: str) -> list[Article]:
        raise NotImplementedError
