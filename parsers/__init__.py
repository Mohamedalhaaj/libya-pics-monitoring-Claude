from __future__ import annotations

from parsers.base import BaseParser
from parsers.feed import FeedListParser
from parsers.generic import GenericListParser


PARSERS: dict[str, type[BaseParser]] = {
    "generic_list": GenericListParser,
    "feed_list": FeedListParser,
}


def get_parser(parser_name: str) -> type[BaseParser]:
    try:
        return PARSERS[parser_name]
    except KeyError as exc:
        available = ", ".join(sorted(PARSERS))
        raise ValueError(f"Unknown parser '{parser_name}'. Available parsers: {available}") from exc
