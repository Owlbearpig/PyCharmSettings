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
import os
from pathlib import Path
import time
import datetime

sql = sql_transfers.MysqlTransfer()
#members = sql.db_get_table('all_members')
current_links = sql.db_get_table('disc_connection')

print(current_links)

