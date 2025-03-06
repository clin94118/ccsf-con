# SPDX-FileCopyrightText: 2024-present clin94118 <clin@ccsf.edu>
#
# SPDX-License-Identifier: MIT
# base imports
import io
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from .ProcessingError import ProcessingError

# required imports
from sqlalchemy import create_engine, text
import pandas as pd
import oracledb
import requests
from cryptography.fernet import Fernet
import configparser

# Global debug flag (turn debug messages on/off)
G_DEBUG_FLAG = False


def debug_print(in_message, in_debug_flag=G_DEBUG_FLAG):
    """Prints all debug messages depending on setting in in_debug_flag

    :param in_message: string to print
    :param in_debug_flag: true or false to print
    """
    if in_debug_flag:
        print(in_message)


def export_csv(df):
    with io.StringIO() as buffer:
        df.to_csv(buffer, index=False, encoding="utf-8")
        return buffer.getvalue()


EXPORTERS = {"dataframe.csv": export_csv}


def get_with_default(in_conf, in_section, in_key, default=None):
    """
    Retrieve configuration values from INI file

    Parameters:
    in_conf (str): loaded configparser
    in_section (str): section header
    in_key (str): key of entry
    default (obj): default value if section/key is not found
    Returns:
    string value retrieved using section and key parameters
    """

    return_val = default

    try:
        return_val = in_conf.get(in_section, in_key)
    except configparser.NoOptionError:
        ProcessingError(f"No such option: {in_key}")
    except configparser.NoSectionError:
        ProcessingError(f"No such section: {in_section}")
    finally:
        return return_val


def get_login(in_file, in_ver, in_fileType="JSON"):
    """
    Retrieve login from JSON file

    Parameters:
    in_file (str): filename of login file
    in_ver (str): version matching required
    in_fileType (str): JSON or INI depending on file type required
    Returns:
    JSON: list of dictionaries containing login details
    INI: Configparser class reading ini file

    Raises:
    FileNotFoundError: The file is not found in current working directory or home/.logins directory
    ValueError: Version in file does not match requirement
    """
    l_file_path = Path.cwd() / in_file

    if not l_file_path.is_file():
        l_file_path = Path.home() / ".logins" / in_file

    if not l_file_path.is_file():
        raise FileNotFoundError(
            f"JSON file '{in_file}' not found in the current directory or home/.logins directory."
        )
    else:
        # Print the file path before opening it
        debug_print(f"Using file file path: {l_file_path}")

    config = {}
    if in_fileType == "JSON":
        with l_file_path.open("r") as json_file:
            config = json.load(json_file)

        if config.get("version") != in_ver:
            raise ValueError(
                f"Unsupported JSON version: {config.get('version')}. Expected version '{in_ver}'."
            )
    elif in_fileType == "INI":
        config = configparser.ConfigParser()
        config_file_path = Path.cwd() / in_file

        if not config_file_path.is_file():
            config_file_path = Path.home() / ".logins" / in_file

        config.read(config_file_path)
    else:
        config = None

    return config


def f_create_wString(in_serStr):
    """series of string converted to filter for sql in statement ('a', 'b', 'c', ...)

    :param in_serStr: string series
    :return: string matching filter in statement
    """
    return_val = "('" + "', '".join(in_serStr) + "')"

    return return_val


def f_print_time():
    """current date string with time

    :return: current time format "%Y-%m-%d %H:%M:%S"
    """
    dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return dt_string


def f_split_df(in_df, in_nGrp):
    """separates in_df into list of dataframes for improved processing

    :param in_df: dataframe to process
    :param in_nGrp: split number in each grouping
    :return: list_df: list of dataframes
    """
    l_numReq = in_df.shape[0]
    list_df = [in_df[i : i + in_nGrp] for i in range(0, l_numReq, in_nGrp)]

    return list_df
