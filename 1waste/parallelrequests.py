import asyncio
import concurrent.futures
from aiohttp import request

class ParallelRequests():
    def __init__(self):
        self.responses = []

    async def main(self, urls):
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    request,
                    url
                )
                for url in urls
            ]
            for response in await asyncio.gather(*futures):
                self.responses.append(response.json())
                pass

    def get_responses(self, urls):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main(urls))
        return self.responses