import time
import asyncio

class RateLimiter():
    RATE = 1000
    MAX_TOKENS = 1000

    def __init__(self, session):
        self.session = session
        self.tokens = self.MAX_TOKENS
        self.updated_at = time.monotonic()

    async def get(self, *args, **kwargs):
        await self.wait_for_token()
        return await self.session.get(*args, **kwargs)

    async def wait_for_token(self):
        while self.tokens <= 1:
            self.add_new_tokens()
            await asyncio.sleep(1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if new_tokens > 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.updated_at = now