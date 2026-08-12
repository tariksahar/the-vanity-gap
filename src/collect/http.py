"""Polite HTTP client shared by every collector.

Implements the rate-limiting contract: a fixed minimum interval between
requests, exponential backoff on any non-200, a descriptive User-Agent, and no
parallelism beyond a small fixed pool. Nothing here knows about any particular
retailer.
"""

from __future__ import annotations

import gzip
import random
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

USER_AGENT = (
    "vanity-gap-research/0.1 (academic study of clothing size labels; "
    "contact: tariksaharr@gmail.com)"
)

# Production default. Phase 0 observed no throttling at 2-4 req/s over ~180
# requests, but that is a small sample and is not a licence to go fast.
DEFAULT_MIN_INTERVAL = 1.0


class FetchError(Exception):
    """Raised when a URL could not be retrieved after all retries."""

    def __init__(self, url: str, status: int | None, message: str):
        super().__init__(f"{url} -> {status}: {message}")
        self.url = url
        self.status = status


@dataclass
class RateLimiter:
    """Enforces a minimum wall-clock interval between requests, thread-safely.

    A single limiter instance is shared by every worker, so the interval is a
    global budget rather than a per-worker one. With one worker and an interval
    of 1.0 this is exactly 1 request per second.
    """

    min_interval: float = DEFAULT_MIN_INTERVAL
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _next_allowed: float = field(default=0.0, repr=False)

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            if now < self._next_allowed:
                delay = self._next_allowed - now
            else:
                delay = 0.0
            self._next_allowed = max(now, self._next_allowed) + self.min_interval
        if delay > 0:
            time.sleep(delay)

    def penalise(self, seconds: float) -> None:
        """Push the next allowed request further out after a server complaint."""
        with self._lock:
            self._next_allowed = max(self._next_allowed, time.monotonic() + seconds)


class Fetcher:
    """Rate-limited GET with exponential backoff.

    Retries on transport errors and on 5xx / 429. Does not retry on other 4xx:
    a 404 is a fact about the URL, not a transient failure, and retrying it
    only wastes the request budget.
    """

    def __init__(
        self,
        limiter: RateLimiter | None = None,
        *,
        max_attempts: int = 4,
        timeout: float = 30.0,
        backoff_base: float = 2.0,
    ):
        self.limiter = limiter or RateLimiter()
        self.max_attempts = max_attempts
        self.timeout = timeout
        self.backoff_base = backoff_base
        self.stats = {"requests": 0, "retries": 0, "failures": 0, "statuses": {}}

    def _record(self, status: int | str) -> None:
        key = str(status)
        self.stats["statuses"][key] = self.stats["statuses"].get(key, 0) + 1

    def get(self, url: str) -> bytes:
        """Fetch a URL and return the decompressed response body."""
        last_status: int | None = None
        last_message = "no attempt made"

        for attempt in range(self.max_attempts):
            self.limiter.wait()
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept-Encoding": "gzip",
                    "Accept": "*/*",
                },
            )
            self.stats["requests"] += 1
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = response.read()
                    if response.headers.get("Content-Encoding") == "gzip":
                        body = gzip.decompress(body)
                    self._record(response.status)
                    return body
            except urllib.error.HTTPError as exc:
                last_status, last_message = exc.code, exc.reason or ""
                self._record(exc.code)
                # Back off hard on throttling or server trouble; give up on the
                # rest of the 4xx range, which will not become true by waiting.
                if exc.code not in (429, 500, 502, 503, 504):
                    break
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                if retry_after and retry_after.isdigit():
                    self.limiter.penalise(float(retry_after))
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_status, last_message = None, repr(exc)
                self._record("transport-error")

            if attempt < self.max_attempts - 1:
                self.stats["retries"] += 1
                # Full jitter, so a burst of simultaneous failures does not
                # retry in lockstep.
                sleep_for = random.uniform(0, self.backoff_base ** (attempt + 1))
                time.sleep(sleep_for)

        self.stats["failures"] += 1
        raise FetchError(url, last_status, last_message)

    def get_text(self, url: str, encoding: str = "utf-8") -> str:
        return self.get(url).decode(encoding, errors="replace")
