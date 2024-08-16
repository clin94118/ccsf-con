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
* f_create_wString(in_str)
* f_print_time()
* f_split_df(in_df, in_nGrp)

### submodules
* oracledb_con
  * class OracleCloudDB
    * connect(self, connection_name, retries=3, delay=5) --creates connection to database
    * execute_sql(self, sql, params=None) -- open cursor execute sql return as dataframe then close cursor
    * close_connection(self) -- close connection to database

## License

`ccsf-con` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
