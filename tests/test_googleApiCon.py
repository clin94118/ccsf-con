import pytest
from ccsf_con import googleApiCon as googleApiCon

@pytest.fixture
def in_googlecon():
    return_val = googleApiCon.googleApiCon()
    return return_val;

def test_list_users(in_googlecon):
    output = in_googlecon.list_users()

    assert len(output) == 5
