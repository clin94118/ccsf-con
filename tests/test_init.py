import pytest
from ccsf_con import f_print_time, f_split_df
from datetime import datetime
import pandas as pd

@pytest.fixture
def my_df():
    return pd.DataFrame({"foo_id": [1, 2, 3, 4, 5, 6]})

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