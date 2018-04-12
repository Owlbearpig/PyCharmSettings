import json
import pymysql
import discord
import asyncio
import aiohttp
from yarl import URL
from files import sql_transfers
from files import variables, asyncrequests, player_char_lookup
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import numpy as np
import requests
import urllib


async def run(url):
    session = aiohttp.ClientSession()
    print(URL(url, encoded=False))
    res = await session.get(URL(url, encoded=False))
    await session.close()
    print(await res.read())

url_list = ["https://raider.io/api/v1/characters/profile?region=eu&realm=Defias%20Brotherhood&name=Uglebj\xf8rnso&fields=mythic_plus_weekly_highest_level_runs"]

loop = asyncio.get_event_loop()

loop.run_until_complete(run(url_list[0]))

#new_req = asyncrequests.ParallelRequestsAsync(loop=loop)

#res = loop.run_until_complete(new_req.get_responses(url_list))







