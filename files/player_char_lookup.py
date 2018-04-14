from files import sql_transfers, asyncrequests, variables
import json
import prettytable
import matplotlib.pyplot as plt
from pathlib import Path
import os

new_variables = variables.Variables()


class AltLookup():

    def __init__(self, disc_id = "105605803632762880"):
        self.disc_id = disc_id
        self.new_variables = variables.Variables()
        mysql_transfer = sql_transfers.MysqlTransfer()
        self.io_requests = asyncrequests.ParallelRequestsAsync()

        self.db_all_chars = json.loads(mysql_transfer.db_get("member_links", "alt_chars", "disc_id={}".format(disc_id))['alt_chars']) # alt chars contains all chars :(

        self.db_dump_main = json.loads(mysql_transfer.db_get("member_links", "main_char", "disc_id={}".format(disc_id))['main_char'])

        self.pic_dimensions = (0,0)


    def url_list_generator(self, char_list, field="mythic_plus_weekly_highest_level_runs"):
        url_list = []
        base_url = self.new_variables._raider_io_base_url
        local_char_list = char_list
        if not type(local_char_list) == type([]): # weird fix ...
            local_char_list = []
            local_char_list.append(char_list)

        for char in local_char_list:
            if char["level"] == 110:
                url_list.append(base_url.format(char["name"], char["realm"], field).replace(" ", "%20"))
        return url_list


    def dungeon_format(self, dungeon_list):
        _dict = {}
        key_words = ["short_name", "mythic_level", "num_keystone_upgrades", "score"]
        if not len(dungeon_list) == 0:
            highest = dungeon_list[0]
            for key in key_words:
                _dict[key] = highest[key]
            _dict["level"] = str(_dict["short_name"])+"+"+str(_dict["mythic_level"])
        else:
            for key in key_words:
                _dict[key] = " "
            _dict["level"] = " "
        return _dict


    def format_response_alt_lookup(self, io_response):
        print(io_response)
        _dict = {}
        key_words = ["name", "active_spec_name", "mythic_plus_weekly_highest_level_runs"]
        for key in key_words:
            _dict[key] = io_response[key]
        _dict["dung"] = self.dungeon_format(_dict["mythic_plus_weekly_highest_level_runs"])
        _dict["weekly_completed"] = " "
        if _dict["dung"]["mythic_level"] != " " and _dict["dung"]["mythic_level"] >= 15:
            _dict["weekly_completed"] = "Yep"
        return _dict

    def spreadsheet(self, *args):
        self.x = prettytable.PrettyTable()

        self.x.field_names = ["Name", "ActiveSpec", "Cap?", "Highest", "Upgrades", "Score"]

        rows = []
        min = 0
        for _list in args:
            rows.extend(_list)
        for _dict in rows:
            self.x.add_row(
                [_dict["name"],
                 _dict["active_spec_name"],
                 _dict["weekly_completed"],
                 _dict["dung"]["level"],
                 _dict["dung"]["num_keystone_upgrades"],
                 _dict["dung"]["score"]]
            )
            if len(_dict["name"]) > min:
                self.pic_dimensions = (len(_dict), len(_dict["name"]))

        self.x.align["Name"] = "l"
        self.x.align["ActiveSpec"] = "l"
        self.x.align["Cap?"] = "l"
        self.x.align["Highest"] = "l"
        self.x.align["Score"] = "r"

    def make_png(self):
        x_dim = self.pic_dimensions[0]
        y_dim = self.pic_dimensions[1]
        x_ratio = 5/8.9
        y_ratio = 0.01
        plt.rc('figure', figsize=(x_dim*x_ratio, 0.5+y_dim*y_ratio))
        plt.rcParams['savefig.facecolor'] = "black"
        ax = plt.gca()
        ax.cla()
        plt.text(0, 0, str(self.x), {'fontsize': 10}, fontproperties='monospace', color = 'white', backgroundcolor = 'black')
        plt.axis('off')
        plt.tight_layout()
        save_path = os.path.join(Path(__file__).parents[1], 'output', 'output-{}.png'.format(self.disc_id))
        plt.savefig(save_path, bbox_inches = 'tight')
        return save_path

if __name__ == '__main__':
    _new = AltLookup()

    _new.spreadsheet([{"abe":123, "bae":324, "312":123, "43":123, "87":123, "3":123,}], [{"asd":123, "htg":64544, "abe":123, "54":123, "521":123, "6":123,}, {"52":123,"5":123,"23":123,"abe":123,"hjg":732, "rew":435}])

    _new.make_png()


