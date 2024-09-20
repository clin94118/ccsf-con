# %%
import pytest
import requests
from ccsf_con import apiCon as apiCon


@pytest.fixture
def in_section():
    return "CANVAS"

def test_create_class(in_section):
    my_api = apiCon.ApiCon(in_section)

    assert my_api._api_name == "CANVAS"

def test_connect_api(in_section):
    my_api = apiCon.ApiCon(in_section)

    myHeader = {f"Authorization": f"Bearer {my_api.get_token()}"}
    my_api.header = myHeader

    my_api.application_path = "/users/%i/page_views"

    myURL = my_api.get_url() % 213288

    my_request = requests.get(myURL, headers=my_api.get_header())

    assert my_request.status_code == 200