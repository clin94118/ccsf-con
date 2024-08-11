# SPDX-FileCopyrightText: 2024-present clin94118 <clin@ccsf.edu>
#
# SPDX-License-Identifier: MIT
# base imports
import os
import sys
import time
from datetime import datetime, timedelta

# required imports
from sqlalchemy import create_engine, text
import pandas as pd
import pyodbc
import oracledb
import cx_Oracle
import requests

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
    list_df = [in_df[i:i+in_nGrp] for i in range(0, l_numReq, in_nGrp)]

    return list_df



# import login information
if sys.platform == 'linux':
    l_login_path = '/home/' + os.getlogin() + '/.logins'
else:
    l_login_path = 'c:/Users/' + os.getlogin() + '/.logins'

sys.path.append(l_login_path)
import DB_LOGIN, IPQS_LOGIN