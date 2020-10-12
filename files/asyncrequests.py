import asyncio
import aiohttp
from aiohttp import ClientSession
from files.aiohttp_ratelimit import RateLimiter
from yarl import URL


class ParallelRequests():

    def __init__(self, loop=None):
        loop = None
        if loop is None: # no loop -> sync code context
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

    async def fetch(self, url, session):
        retries = 10
        #print(URL(url, encoded=False))
        try:
            response = await session.get(URL(url, encoded=False))
            for retry in range(retries):
                if response.status != 200:
                    if response.status == 404:
                        print("    ",str(url.replace(" ", "%20")), response.status)
                        return
                    print("    ",str(url.replace(" ", "%20")), response.status, "Retrying:", retry, "/", retries)
                    response = await session.get(URL(url, encoded=False))
                else:
                    return await response.read()
            print(url, "could not be fetched")
            return
        except:
            pass

    async def bound_fetch(self, sem, url, session):
        async with sem:
            return await self.fetch(url, session)

    async def run(self, url_list):
        tasks = []
        sem = asyncio.Semaphore(1000)

        async with ClientSession() as session:
            # session = RateLimiter(session) # retrying instead of rate limiting : )
            for url in url_list:
                task = asyncio.ensure_future(self.bound_fetch(sem, url, session))
                tasks.append(task)

            self.responses = await asyncio.gather(*tasks)


class ParallelRequestsSync(ParallelRequests):
    def get_responses(self, url_list):
        loop = self.loop
        future = asyncio.ensure_future(self.run(url_list), loop=loop)
        loop.run_until_complete(future)
        return self.responses


class ParallelRequestsAsync(ParallelRequests):
    async def get_responses(self, url_list):
        await self.run(url_list)
        return self.responses


if __name__ == '__main__':


    member_list = [{"name": "owlbearpig", "realm": "defias brotherhood"},
                   {'name': 'Necrodude', 'realm': 'Scarshield Legion'},
                   {'name': 'Sharft', 'realm': 'Scarshield Legion'}, {'name': 'Tobi', 'realm': 'Scarshield Legion'},
                   {'name': 'Khakuzu', 'realm': 'Scarshield Legion'}]

    base_url = "https://eu.api.battle.net/wow/character/{1}/{0}?locale=en_GB&apikey=2jgcc3hu793728swxja8zryxhsq69j9e"

    url_list = []

    for member in member_list:
        url_list.append(base_url.format(member["name"], member["realm"]))

    new_parallel_request = ParallelRequestsSync()

    responses = new_parallel_request.get_responses(url_list)

    responses = [response.decode("utf-8") for response in responses if response != None]
    print(responses)
