from files import sql_transfers
from files.variables import Variables
import json

new_vars = Variables()
disc_id_dict = new_vars._disc_dict

new_sql_transfer = sql_transfers.MysqlTransfer()

db_dump = new_sql_transfer.db_get_table("all_members")

def get_dict_matches(**kwargs):
    # if len(matches) == 1, returns single match, else list of matches. Problem: should return always be list ? ??
    matches = []
    for _dict in db_dump:
        if all([_dict[key] == kwargs[key] for key in kwargs]):
            matches.append(_dict)

    if len(matches) == 1:
        return matches[0]
    return matches


def create_member_links():
    mains = []
    for disc_id in disc_id_dict:
        mains.append(get_dict_matches(name=disc_id_dict[disc_id][0], realm=disc_id_dict[disc_id][1]))
        mains[len(mains)-1:len(mains)][0]["disc_id"] = disc_id

    linked_tuples = []
    for _main in mains:
        linked_tuples.append((_main, get_dict_matches(achieve_id=_main["achieve_id"])))

    for link in linked_tuples:
        _main = json.dumps(link[0])
        _alts = json.dumps(link[1])
        data = {"main_char" : _main, "alt_chars" : _alts, "disc_id" : link[0]["disc_id"]}
        new_sql_transfer.versatile_db_store(**data, single_store=False, table="member_links")

    new_sql_transfer.connection.commit()

create_member_links()
