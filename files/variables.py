import os
from pathlib import Path

class Variables():

    def __init__(self):

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