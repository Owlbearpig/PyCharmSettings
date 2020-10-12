import requests

class GenTbMemberList():

    def __init__(self):
        # Variables

        # url GET Members /wow/guild/:realm/:guildName
        self.blizzguildrequrl = "https://eu.api.battle.net/wow/guild/defias%20brotherhood/the%20betrayed?fields=members&locale=en_GB&apikey=2jgcc3hu793728swxja8zryxhsq69j9e"

        # url GET achievements member/realm
        self.blizzachievrequrl = "https://eu.api.battle.net/wow/character/{1}/{0}?fields=achievements&locale=en_GB&apikey=2jgcc3hu793728swxja8zryxhsq69j9e"

        self.member_dict = {}

        # make list on initialization
        self.make_list()

    def get_guild_members(self):
        self.members = requests.get(self.blizzguildrequrl).json()["members"]

    def make_list(self):
        self.get_guild_members()
        for member in self.members:
            if member["character"]["level"] >= 10:
                self.member_dict[str(member["character"]["name"]) + " " + str(member["character"]["realm"])] = \
                    {
                        "name"        : member["character"]["name"],
                        "realm"       : member["character"]["realm"],
                        "class"       : member["character"]["class"],
                        "level"       : member["character"]["level"],
                        "achieve_pts" : member["character"]["achievementPoints"],
                        "g_rank"      : member["rank"]
                    }

    def format_blizz_char_response(self, blizz_char_response_dict_list):
        member_dict = {}
        for member in blizz_char_response_dict_list:
            try:
                member_dict[str(member["name"]) + " " + str(member["realm"])] = \
                    {
                        "name"        : member["name"],
                        "realm"       : member["realm"],
                        "class"       : member["class"],
                        "level"       : member["level"],
                        "achieve_pts" : member["achievementPoints"],
                        "achieve_id"  : str(sum(member["achievements"]["achievementsCompletedTimestamp"]))
                    }
            except Exception as e:
                print(member)
                print(e)
        return member_dict

