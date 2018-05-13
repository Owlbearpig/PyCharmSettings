import os
from pathlib import Path

class Variables():

    def __init__(self):

        self._disc_dict = {"232637566539530242": ("Endavar", "Defias Brotherhood"), "105605803632762880": ("Rushb", "Defias Brotherhood"),
                     "230409217427636246": ("Skifi", "Defias Brotherhood"), "200148751040380932": ("Aksandria", "Defias Brotherhood"),
                     "261515660373393408": ("Randygoat", "Defias Brotherhood"), "197408009993977856": ("Kosshi", "Defias Brotherhood"),
                     "186576608205733889": ("Owlbearpig", "Defias Brotherhood"), "244455075567763457": ("Daddy", "Ravenholdt"),
                           "377814093031014400": ("Agradié", "Defias Brotherhood"), "158649901755006986": ("Walakvafan", "Defias Brotherhood"),
                           "247032881799495680": ("Drooka", "Defias Brotherhood"), "329718786150236170": ("Morthrang", "Defias Brotherhood"),
                           "126756935369228289": ("Wallaboop", "Defias Brotherhood"), "256124331115937792": ("Rhøme", "Defias Brotherhood"),
                           "111591538370359296": ("Qulmi", "Defias Brotherhood"), "228977675962679296": ("Dæth", "Scarshield Legion"),
                           "186920089608519680": ("Moistman", "Defias Brotherhood"), "205382564846895106": ("Dalatu", "Defias Brotherhood"),
                           "328938870819258378": ("Napadai", "The Venture Co"), "205052050621464578": ("Eilá", "Defias Brotherhood"),
                           "209749672577859586": ("Deagan", "Defias Brotherhood"), "98907917826142208": ("Equalism", "Defias Brotherhood"),
                           "228206751189565441": ("Shanist", "Defias Brotherhood"), "136494225335386112": ("Vurx", "Defias Brotherhood"),
                           "86959058623430656": ("Kuard", "Defias Brotherhood")
                           }

        self._raider_io_base_url = "https://raider.io/api/v1/characters/profile?region=eu&realm={1}&name={0}&fields={2}"

        self.login_data = self.read_local_logins()

        self._disc_login_token = self.get_disc_token()

    def get_disc_token(self):
        return self.login_data["disctoken"]

    def get_mysql_login(self):
        return self.login_data["mysql_login_info"]

    def read_local_logins(self):
        _login_info_path = os.path.join(Path(__file__).parents[0], "login_info")
        f = open(_login_info_path)
        return eval(f.read())


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass