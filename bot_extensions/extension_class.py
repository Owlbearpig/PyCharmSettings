import asyncio
import csv
import json
from files import dungeonator_standalone, player_char_lookup
import os.path
from pathlib import Path
from files import asyncrequests
from files import sql_transfers

class BotExtensionFunctions():
    def __init__(self, loop = None):
        self.loop = loop
        self.altinator_png_path = os.path.join(Path(__file__).parents[1], 'files', 'placeholder.jpg')

    @asyncio.coroutine
    async def dungeonator_main(self):
        output_str = [["name", "rank", "week cap", "highest dung+level", "chests",
                   "completion date", "prev week completed", "prev week cap dung", "completed at:"]]
        new_chk = dungeonator_standalone.MythicPlusCheck(loop=self.loop)
        g_member_list = await new_chk.g_member_list_get()

        failed_requests_chars = []
        fail = False
        for char in g_member_list:
            try:
                response = await new_chk.get_IOinfo(char)
                print("\n")
            except Exception as e:
                print(e)
                retry_delay = 30
                print("\n# of api calls limited. Waiting {} s before retrying".format(retry_delay))
                await asyncio.sleep(retry_delay)
                try:
                    response = await new_chk.get_IOinfo(char)
                except:
                    print("couldn't get char :( adding to retries")
                    failed_requests_chars.append(char)
            if char not in failed_requests_chars:
                output_str.append(new_chk.format_response(IOresponse_cur=response[0], IOresponse_prev=response[1], guildrank=response[2]))

        if not len(failed_requests_chars) == 0:
            print("retrying failed requests once:", failed_requests_chars)
            for failed_char in failed_requests_chars:
                try:
                    response = await new_chk.get_IOinfo(char=failed_char)
                    output_str.append(new_chk.format_response(IOresponse_cur=response[0], IOresponse_prev=response[1], guildrank=response[2]))
                except:
                    print(failed_char, "couldn't be fetched. Giving up")

        with open("out.csv", "w") as file:
            wr = csv.writer(file)
            wr.writerows(output_str)
        print("file generated")


    @asyncio.coroutine
    async def lookup_routine(self, alt_lookup):
        new_lookup = alt_lookup

        db_all_chars_temp = new_lookup.db_all_chars
        db_all_chars_temp.remove(new_lookup.db_dump_main)

        url_alts = new_lookup.url_list_generator(db_all_chars_temp)
        url_main = new_lookup.url_list_generator(new_lookup.db_dump_main)

        res_alts = await new_lookup.io_requests.get_responses(url_alts)
        res_main = await new_lookup.io_requests.get_responses(url_main)

        alt_char_responses = [json.loads(char.decode("utf-8")) for char in res_alts]
        main_char_response = [json.loads(char.decode("utf-8")) for char in res_main]

        formatted_responses = []
        for io_response_char in main_char_response + alt_char_responses:
            formatted_responses.append(new_lookup.format_response_alt_lookup(io_response=io_response_char))
        new_lookup.spreadsheet(formatted_responses)

        self.altinator_png_path = new_lookup.make_png()
        print(self.altinator_png_path)

    @asyncio.coroutine
    async def add_disc_user(self, new_char, disc_id):
        def is_connected(new_char):
            res = False
            current_links = sql.db_get_table('disc_connection')
            for connection in current_links:
                if connection["name"].lower() == new_char.lower():
                    res = True
            return res

        sql = sql_transfers.MysqlTransfer()
        members = sql.db_get_table('all_members')
        if is_connected(new_char=new_char):
            return 2 # already in db ...

        for member in members:
            print(new_char.lower(), member["name"].lower())
            if new_char.lower() == member["name"].lower():
                sql.versatile_db_store(**{"disc_id" : disc_id, "name": member["name"], "realm": member["realm"]}, table="disc_connection")
                return None # success

        return 1 # probably couldn't be found in guild db



    @asyncio.coroutine
    async def altinator_main(self, disc_id="105605803632762880"):

        res = False
        new_lookup = player_char_lookup.AltLookup(disc_id=disc_id)

        if new_lookup.id_is_present:
            res = True
            await self.lookup_routine(new_lookup)
        return res


