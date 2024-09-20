import configparser
from pathlib import Path
import requests
from ccsf_con import get_with_default

API_INI_FILE = "api.ini"
API_INI_FILE_SUPPORTED = "0.5"


class ApiCon:
    """
    A class to manage api operations, retrieving token and url paths from ini file
    """

    def __init__(self, api_name, debug=False, ini_file=API_INI_FILE):
        """
        Parameters
        ----------
        in_api: str
            section of ini containing

        """
        config = configparser.ConfigParser()
        config_file_path = Path.cwd() / ini_file

        if not config_file_path.is_file():
            config_file_path = Path.home() / ".logins" / ini_file

        if not config_file_path.is_file():
            raise FileNotFoundError(
                f"Ini file '{ini_file}' not found in the current directory or home/.logins directory."
            )
        else:
            if debug:
                print(f"Using INI file path: {config_file_path}")

        config.read(config_file_path)

        if get_with_default(config, "DEFAULT", "version") != API_INI_FILE_SUPPORTED:
            raise ValueError(
                f"Unsupported INI version: {config.get('DEFAULT', 'version')}. Expected version '{in_ver}'."
            )

        self._api_name = api_name
        self._token = get_with_default(config, api_name, "token")
        self._username = get_with_default(config, api_name, "username")
        self._password = get_with_default(config, api_name, "password")
        self._gen_endpt = get_with_default(config, api_name, "end_point")
        self.application_path = ""
        self.settings = ""
        self.header = {"Accept": "application/json", "Content-Type": "application/json"}

        if self._api_name == "COMEVO":
            payload = f"grant_type=password&username={self._username}&password={self._password}"
            response = requests.post(f"{self._gen_endpt}/token", headers=self.header, data=payload)

            if response.status_code == 200:
                response = response.json()
                self._token = response["access_token"]
            else:
                print("Comevo token access failed: {response.status_code}")

    def get_token(self):
        return self._token

    def get_header(self):
        return self.header

    def get_endpt(self):
        return self._gen_endpt

    def get_application_path(self):
        return self.application_path

    def get_settings(self):
        return self.settings

    def get_url(self):
        return_val = f"{self._gen_endpt}{self.application_path}{self.settings}"

        return return_val
