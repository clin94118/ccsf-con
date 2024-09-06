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
* get_login(in_file, in_ver, debug = False) -- take json file and return list of dictionaries with data
* f_create_wString(in_str) -- convert list of string into filter for sql statement ('a', 'b', 'c', ...)
* f_print_time() -- print current time in format "%Y-%m-%d %H:%M:%S"
* f_split_df(in_df, in_nGrp) -- split dataframe into list of nGrp size dataframes 

### submodules
* oracledb_con
  * class OracleCloudDB
    * connect(self, connection_name, retries=3, delay=5) --creates connection to database
    * execute_sql(self, sql, params=None) -- open cursor execute sql return as dataframe then close cursor
    * close_connection(self) -- close connection to database

## License

`ccsf-con` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
