import csv
import time
import datetime
import json
import asyncio
from files import asyncrequests


class MythicPlusCheck():
    def __init__(self, loop=None):
        # guild ranks to be checked (don't check socials please, or it will run for an eternity lul)
        # 0: gm, 1: officer, 2: raider, 3: rm alt, 4: veteran, 5: trial, 6: smallbreak, 7: alt, 8: muted, 9: social
        self.ranks = [0,1,2,5]

        # blizz api key
        self.key = {"apikey": "2jgcc3hu793728swxja8zryxhsq69j9e"}

        # url for GET Members /wow/guild/:realm/:guildName
        self.blizzrequrl = "https://eu.api.battle.net/wow/guild/defias%20brotherhood/the%20betrayed?fields=members&locale=en_GB"

        # url for get /api/v1/characters/profile params: region, realm{1}, name{0}, fields mythic_plus_weekly_highest_level_runs (mpwhlr)
        self.raiderIOrequrlWeeklyHighest = "https://raider.io/api/v1/characters/profile?region=eu&realm={1}&name={0}&fields=mythic_plus_weekly_highest_level_runs"

        # url for get /api/v1/characters/profile params: region, realm{1}, name{0}, fields mythic_plus_recent_runs
        self.raiderIOrequrlRecentDung = "https://raider.io/api/v1/characters/profile?region=eu&realm={1}&name={0}&fields=mythic_plus_recent_runs"

        self.async_requests = asyncrequests.ParallelRequestsAsync(loop=loop)


    # takes guild member (dict), returns member (dict) if conds are met else (None)
    def _filter(self, member = None):
        excluded_names = ["Scarypotato"]
        conds = [member["character"]["level"] == 110] # everyone must be 110
        conds.extend([member["character"]["name"] != name for name in excluded_names]) # names in excluded_names don't need checking

        if any([member["rank"] == rank for rank in self.ranks]) and all(conds): # if member has any rank in rank and meets all conditions
            return member

    # returns [name (str), realm of members who pass _filter (str), guild rank (int)]
    async def g_member_list_get(self):
        rm_list = []
        self.blizzrequrl += "&apikey=" + self.key["apikey"]
        guild = (await self.async_requests.get_responses([self.blizzrequrl]))[0].decode("utf-8")
        guild = json.loads(guild)

        members = guild["members"]
        for i in range(len(members)):
            member = self._filter(members[i])
            if not member == None:
                rm_list.append([member["character"]["name"], member["character"]["realm"], member["rank"]])
        return rm_list

    # input char (list)
    # returns (weekly_highest (json), recent_dungeons (json), char rank (int))
    async def get_IOinfo(self, char = None): # char = [name, realm, rank]
        print(char[0], char[1], char[2])
        cur_week = (await self.async_requests.get_responses([self.raiderIOrequrlWeeklyHighest.format(char[0], char[1])]))[0].decode("utf-8")
        prev_week = (await self.async_requests.get_responses([self.raiderIOrequrlRecentDung.format(char[0], char[1])]))[0].decode("utf-8")
        return json.loads(cur_week), json.loads(prev_week), char[2]

    # returns #days to next Wednesday (int). (if today is Wed returns 7)
    def days_to_wed(self):
        cur_time = datetime.datetime.today()
        if cur_time.weekday() == 2:
            return 7
        else:
            ctr = 0
            while cur_time.weekday() != 2:
                cur_time = cur_time + datetime.timedelta(days=1)
                ctr += 1
            return ctr

    # returns previous lockout interval (datetime obj, datetime obj)
    def reset_interval(self):
        cur_time = datetime.datetime.today()
        next_reset_day = cur_time + datetime.timedelta(days=self.days_to_wed())
        next_reset = next_reset_day.replace(hour=8, minute=0, second=0)
        cur_reset_start = next_reset - datetime.timedelta(days=7)
        prev_reset_start = cur_reset_start - datetime.timedelta(days=7)
        return prev_reset_start, cur_reset_start

    # input: datetime obj
    # returns datetime object time (int)
    def datetime_to_int(self, datetime = None):
        return int(time.mktime(datetime.timetuple()))

    # input: dung (dict)
    # returns: (date of completion (datetime obj), level (int))
    def dung_info(self, dung = None):
        level = dung["mythic_level"]
        date_raw = dung["completed_at"]
        date = datetime.datetime.strptime(date_raw.replace(".000Z", ""), "%Y-%m-%dT%H:%M:%S")
        return date, level

    # input: from io response (json) IOresponse_prev["mythic_plus_recent_runs"] (list)
    # returns: (dungeon done last reset (bool), dungeon and level (str), time of completion (str))
    def done_last_reset(self, prev_dungs = None):
        interval = self.reset_interval()
        done = "Data N/A"
        label = "Data N/A"
        date = "Data N/A"

        start_prev_reset = self.datetime_to_int(interval[0])
        end_prev_reset = self.datetime_to_int(interval[1])
        for dung in prev_dungs:
            if  self.datetime_to_int(self.dung_info(dung)[0]) < end_prev_reset:
                level = self.dung_info(dung)[1]
                if end_prev_reset > self.datetime_to_int(self.dung_info(dung)[0]) > start_prev_reset and level >= 15:
                    done = True
                    label = "{1}+{0}".format(level, dung["short_name"])
                    date = self.dung_info(dung)[0]
                    return done, label, date
                else:
                    done = False
                    label = None
                    date = None
        return done, label, date

    # input from get_IOinfo. IOresponses (json) and guildrank (int)
    # returns formatted and relevant data from the ioresponse (list)
    def format_response(self, IOresponse_cur = None, IOresponse_prev = None, guildrank = None):
        rank_dict = {
            None : "None",
            0 : "gm",
            1 : "officer",
            2 : "raider",
            3 : "rm alt",
            4 : "veteran",
            5 : "trial",
            6 : "smallbreak",
            7 : "alt",
            8 : "muted",
            9 : "social"
        }
        name = IOresponse_cur["name"]
        dung = IOresponse_cur["mythic_plus_weekly_highest_level_runs"]
        prev_dungs = IOresponse_prev["mythic_plus_recent_runs"]

        prev_week_res = self.done_last_reset(prev_dungs)

        if len(dung) > 0:
            done = dung[0]["mythic_level"] >= 15
            return [name, str(rank_dict[guildrank]), str(done), "{0}+{1}".format(dung[0]["short_name"], dung[0]["mythic_level"]),
                    str(dung[0]["num_keystone_upgrades"]), str(dung[0]["completed_at"]).replace(".000Z", "").replace("T", " "),
                    str(prev_week_res[0]), str(prev_week_res[1]), str(prev_week_res[2])]
        else:
            done = False
            return [name, str(rank_dict[guildrank]), str(done), None,
                    None, None, str(prev_week_res[0]), str(prev_week_res[1]), str(prev_week_res[2])]

if __name__ == '__main__':
    output_str = [["name", "rank", "week cap", "highest dung+level", "chests",
               "completion date", "prev week completed", "prev week cap dung", "completed at:"]]

    loop = asyncio.get_event_loop()

    new_chk = MythicPlusCheck()

    char_list_future = asyncio.ensure_future(new_chk.g_member_list_get(), loop=loop)
    char_list = loop.run_until_complete(char_list_future)

    print("\n################################")
    print("Det er kun muligt at se de tre sidste dungeon runs.\n\nDet betyder hvis en person har lavet tre den her uge,\n"
          "men ingen sidste uge kan man ikke se det -> Data N/A...\n\nMed stor sandsynlighed blev de lavet sidste uge =)")
    print("################################")
    time.sleep(2)
    print("\nchecking guild ranks:", new_chk.ranks, "\n")

    for char in char_list:
        for j in range(10):
            try:
                response_future = asyncio.ensure_future(new_chk.get_IOinfo(char), loop=loop)
                response = loop.run_until_complete(response_future)
                print("\n")
            except Exception as e:
                print(e)
                print("\n# of api calls limited. Retry: {0}/10 \nwaiting 30s before retrying".format(j))
                time.sleep(30)
            else:
                break
        else:
            print("couldn't connect :(")
        output_str.append(new_chk.format_response(IOresponse_cur=response[0], IOresponse_prev=response[1], guildrank=response[2]))
    with open("out.csv", "w") as file:
        wr = csv.writer(file)
        wr.writerows(output_str)
