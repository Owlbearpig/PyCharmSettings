import asyncio
import csv
import json
from files import dungeonator_standalone, player_char_lookup



class BotExtensionFunctions():
    def __init__(self, loop = None):
        self.loop = loop
        self.altinator_png_path = None

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
    async def altinator_main(self, disc_id="105605803632762880"):

        lookup = player_char_lookup.AltLookup(disc_id=disc_id)

        db_all_chars_temp = lookup.db_all_chars
        db_all_chars_temp.remove(lookup.db_dump_main)

        url_alts = lookup.url_list_generator(db_all_chars_temp)
        url_main = lookup.url_list_generator(lookup.db_dump_main)

        res_alts = await lookup.io_requests.get_responses(url_alts)
        res_main = await lookup.io_requests.get_responses(url_main)

        alt_char_responses = [json.loads(char.decode("utf-8")) for char in res_alts]
        main_char_response = [json.loads(char.decode("utf-8")) for char in res_main]

        formatted_responses = []
        for io_response_char in main_char_response + alt_char_responses:
            formatted_responses.append(lookup.format_response_alt_lookup(io_response=io_response_char))
        lookup.spreadsheet(formatted_responses)

        self.altinator_png_path = lookup.make_png()
        print(self.altinator_png_path)

