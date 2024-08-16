import asyncio


import time


from op_core.logger import get_logger

logger = get_logger(__name__)


class AsyncRateLimiter:
    def __init__(self, requests_per_minute: int):
        self.interval = 60 / requests_per_minute
        self.last_request_time = 0
        logger.info(
            f"AsyncRateLimiter initialized with {requests_per_minute} requests per minute"
        )

    async def wait(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.interval:
            sleep_time = self.interval - time_since_last_request
            logger.debug(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()
