import requests
import json
import asyncio
from files import asyncrequests, sql_transfers, tb_member_list

_api_key = "2jgcc3hu793728swxja8zryxhsq69j9e"
_base_url = "https://eu.api.battle.net/wow/character/{1}/{0}?fields={2}&locale=en_GB&apikey=" + _api_key

new_transfer = sql_transfers.MysqlTransfer()

member_list_gen = tb_member_list.GenTbMemberList()

new_members = {}

def is_equal_non_ordered_dicts(dict_a, dict_b):
    bool_list = []
    for key in dict_a:
        bool_list.append(dict_a[key] == dict_b[key])
    if all(bool_list):
        return True
    return False


def member_url_list_gen(member_list):
    url_list = []
    for member in member_list:
        if member["level"] >= 10:
            url_list.append(_base_url.format(member["name"], member["realm"], "achievements"))
        else:
            print(member, "not above level 10")
    return url_list


# sync execution takes forever : (
def blizz_api(name="owlbearpig", realm="defias brotherhood", fields=""):
    res = requests.get(_base_url.format(name, realm, fields))
    return json.dumps(res.json())


def db_update(member_dicts):
    if len(member_dicts) == 0:
        print("All members up to date")
        return

    def db_upload(member):
        new_transfer.store(single_store=False, data=(member["name"],
                            member["realm"],
                            member["class"],
                            member["level"],
                            member["achieve_pts"],
                            member["g_rank"],
                            member["achieve_id"]))

    for member in member_dicts:
        if member in new_blizz_guild_member_dict:
            if member in new_members:
                db_upload(member_dicts[member])
                print("new member:", member, "added to db")
            else:
                db_upload(member_dicts[member])
                print(member, "updated")
        else:
            name = member_dicts[member]["name"], realm = member_dicts[member]["realm"]
            print(name, realm, "is not a guild member -> removing from db")
            new_transfer.remove_entry("all_members", "name=\'{0}\' AND realm=\'{1}\'".format(name, realm))

    new_transfer.connection.commit()
    new_transfer.connection.close()


def append_g_rank_to_members(blizz_char_dict, blizz_guild_member_list):
    member_dict = blizz_char_dict

    def get_g_rank(char):
        for member in blizz_guild_member_list.values():
            if char["name"] == member["name"] and char["realm"] == member["realm"]:
                return member["g_rank"]

    for char in member_dict.values():
        if "g_rank" in char:
            pass
        else:
            member_dict[str(char["name"]) + " " + str(char["realm"])]["g_rank"] = get_g_rank(char)
    return member_dict


def db_dump_format(db_dump_list):
    db_dump_char_dict = {}
    for char in db_dump_list:
        db_dump_char_dict[str(char["name"])+ " " + str(char["realm"])] = char
    return db_dump_char_dict


def find_outdated_entries(db_dump_dict, updated_member_dict):
    updates_of_members = {}
    for key in updated_member_dict:
        if key not in db_dump_dict:
            new_members[key] = updated_member_dict[key]
            updates_of_members[key] = updated_member_dict[key]
        elif not is_equal_non_ordered_dicts(db_dump_dict[key], updated_member_dict[key]):
            updates_of_members[key] = updated_member_dict[key]

    return updates_of_members

print("Getting new guild member dict")
new_blizz_guild_member_dict = member_list_gen.member_dict

print("Requesting achievement/character data for every guild member")
new_requests = asyncrequests.ParallelRequestsSync()
char_response_data = new_requests.get_responses(member_url_list_gen(new_blizz_guild_member_dict.values()))

print("Formatting response")
new_blizz_char_list = [json.loads(i.decode("utf-8")) for i in char_response_data if i != None]
new_blizz_char_dict = member_list_gen.format_blizz_char_response(blizz_char_response_dict_list=new_blizz_char_list)

print("Appending g_ranks to characters in the new character list")
final_updated_member_list = append_g_rank_to_members(new_blizz_char_dict, new_blizz_guild_member_dict)

print("Getting all_members table from sql db")
db_dump = new_transfer.db_get_table("all_members")

print("Formatting db dump")
db_dump = db_dump_format(db_dump)

print("Searching for outdated entries")
updates = find_outdated_entries(db_dump, final_updated_member_list)

print("Uploading updated entries")
db_update(updates)

