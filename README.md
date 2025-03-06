# ccsf_con

[![PyPI - Version](https://img.shields.io/pypi/v/ccsf-con.svg)](https://pypi.org/project/ccsf-con)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ccsf-con.svg)](https://pypi.org/project/ccsf-con)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Overview

## Installation

```console
pip install ccsf-con
```

## Processes
### Base Functions
* debug_print(in_message) -- print based on G_DEBUG_FLAG
* get_with_default(in_conf, in_section, in_key, default = None) -- retrieve values from an INI file
* get_login(in_file, in_ver, debug = False) -- take json file and return list of dictionaries with data
* f_create_wString(in_str) -- convert list of string into filter for sql statement ('a', 'b', 'c', ...)
* f_print_time() -- print current time in format "%Y-%m-%d %H:%M:%S"
* f_split_df(in_df, in_nGrp) -- split dataframe into list of nGrp size dataframes 

### submodules
* oracleDbCon
  * class OracleCloudDB
    * connect(self, connection_name, retries=3, delay=5) --creates connection to database
    * execute_sql(self, sql, params=None) -- open cursor execute sql return as dataframe then close cursor
    * close_connection(self) -- close connection to database
* googleApiCon 
  * class  GoogleApiCon
    * authenticate(self) --authenticates Google Admin service account
    * list_users(self, num_records=5) -- list of users in domain
    * create_user(self, email, password, first_name, last_name, org_unit_path=PREREG_OU, max_wait_time=5) -- create email user
    * get_user(self, email) -- retrieve json detail for specific user
    * get_user_ouPath(self, email) -- retrieve organizational unit path of user
    * get_last_login_date(self, email) -- retrieve last login of user (if no login then default to "1970-01-01T00:00:00.000Z")
    * update_user_name(self, email, new_given_name, new_family_name) -- change first (given) and last name (family) of user
    * update_user_password(self, email, new_password) -- update password for user
    * update_user_ouPath(self, email, new_ou) -- move user to new organizational unit
    * delete_user(self, email, max_wait_time=60, check_interval=1) -- delete user by email address
* apiCon
  * class ApiCon
    * get_token(self) -- retrieve token
    * get_header(self) -- retrieve header
    * get_endpt(self) -- retrieve primary end_point
    * get_application_path(self) -- retrieve application path
    * get_settings(self) -- retrieve settings
    * get_url(self) -- returns end_point, application path, and setting as string


## License

`ccsf-con` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
