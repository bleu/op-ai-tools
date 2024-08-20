import asyncio
from typing import Optional, Dict, Any
import aiohttp
from op_data.utils.rate_limiter import AsyncRateLimiter

from op_core.logger import get_logger

logger = get_logger(__name__)


class BaseScraper:
    def __init__(self, base_url: str, requests_per_minute: int = 60):
        self.base_url = base_url
        self.rate_limiter = AsyncRateLimiter(requests_per_minute)

    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        await self.rate_limiter.wait()

        logger.debug(f"Making {method} request to {url}")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method, url, params=params, json=data, headers=headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    raise
                logger.error(f"HTTP error occurred: {e}")
                raise
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise

    async def retry_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 15,
    ) -> Dict[str, Any]:
        for attempt in range(max_retries):
            try:
                return await self.make_request(endpoint, method, params, data, headers)
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Too Many Requests
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(
                        f"Rate limit exceeded. Retrying in {wait_time} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
        logger.error(f"Max retries reached for endpoint: {endpoint}")
        raise Exception(
            f"Failed to fetch data from {endpoint} after {max_retries} attempts"
        )
