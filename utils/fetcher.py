from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from playwright.async_api import Browser, Page, async_playwright

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FetchResult:
    url: str
    html: str
    final_url: str


class BrowserFetcher:
    def __init__(
        self,
        timeout_ms: int = 30000,
        retries: int = 3,
        retry_delay_seconds: float = 2.0,
        headless: bool = True,
    ) -> None:
        self.timeout_ms = timeout_ms
        self.retries = retries
        self.retry_delay_seconds = retry_delay_seconds
        self.headless = headless
        self._playwright = None
        self._browser: Browser | None = None

    async def __aenter__(self) -> "BrowserFetcher":
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        return self

    async def __aexit__(self, *_args: object) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def fetch(self, url: str, wait_for_selector: str | None = None) -> FetchResult:
        if not self._browser:
            raise RuntimeError("BrowserFetcher must be used as an async context manager")

        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            page: Page | None = None
            try:
                page = await self._browser.new_page()
                page.set_default_timeout(self.timeout_ms)
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=self.timeout_ms)
                html = await page.content()
                return FetchResult(url=url, html=html, final_url=page.url)
            except Exception as exc:  # Playwright raises several transport-specific subclasses.
                last_error = exc
                logger.warning("Fetch failed for %s on attempt %s/%s: %s", url, attempt, self.retries, exc)
                if attempt < self.retries:
                    await asyncio.sleep(self.retry_delay_seconds * attempt)
            finally:
                if page:
                    await page.close()

        raise RuntimeError(f"Failed to fetch {url} after {self.retries} attempts") from last_error
