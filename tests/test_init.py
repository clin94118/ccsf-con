import pytest
from pathlib import Path
from datetime import datetime
import pandas as pd
import configparser
from unittest.mock import patch, call

from ccsf_con import (
    debug_print, f_print_time, f_split_df, f_create_wString,
    get_login, get_with_default
)

API_INI_FILE = "api.ini"
API_INI_FILE_SUPPORTED = "0.5"


@pytest.fixture
def my_df():
    return pd.DataFrame({"foo_id": [1, 2, 3, 4, 5, 6]})


@pytest.fixture
def config_parse():
    return_val = configparser.ConfigParser()

    config_file_path = Path.cwd() / API_INI_FILE

    if not config_file_path.is_file():
        config_file_path = Path.home() / ".logins" / API_INI_FILE

    if not config_file_path.is_file():
        raise FileNotFoundError(
            f"Ini file '{API_INI_FILE}' not found in the current directory or home/.logins directory."
        )

    return_val.read(config_file_path)

    return return_val


@patch('builtins.print')
def test_debug_print(mock_print):

    debug_print('Test', True) # prints
    debug_print('No Print', False) # no print

    assert mock_print.mock_calls == [call('Test')]


def test_f_print_time():
    assert f_print_time() == datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def test_f_split_df(my_df):
    test_grp = f_split_df(my_df, 3)

    verify_df1 = pd.DataFrame({"foo_id": [1, 2, 3]})
    verify_df2 = pd.DataFrame({"foo_id": [4, 5, 6]})
    verify_df2 = verify_df2.set_index(pd.Series([3, 4, 5]))
    verify_grp = [verify_df1, verify_df2]

    for i in range(len(test_grp)):
        pd.testing.assert_frame_equal(test_grp[i], verify_grp[i])


def test_f_create_wString(my_df):
    gen_list = list(my_df.foo_id.astype(str))
    wString = f_create_wString(gen_list)
    assert wString == "('1', '2', '3', '4', '5', '6')"


def test_get_login_json():
    conns = get_login('.DbConnections.json', '1.01')
    con_df = pd.DataFrame.from_dict(conns.get('connections'), orient="columns")

    l_filter = con_df["name"] == 'OCI_PPRD'
    assert len(con_df[l_filter]) > 0

def test_get_login_ini():
    conns = get_login('api.ini', '0.5', "INI")

    service_account_email = get_with_default(conns, "GOOGLE", "service_account_email")

    assert service_account_email == "ce_ansel.adams@mail.ccsf.edu"

def test_get_with_default(config_parse):
    curVer = get_with_default(config_parse, "DEFAULT", "version")

    assert curVer == API_INI_FILE_SUPPORTED
