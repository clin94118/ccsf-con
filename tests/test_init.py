import pytest
from ccsf_con import f_print_time, f_split_df, f_create_wString
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

def test_f_create_wString(my_df):
    gen_list = list(my_df.foo_id.astype(str))
    wString = f_create_wString(gen_list)
    assert wString == "('1', '2', '3', '4', '5', '6')"