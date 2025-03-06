import pytest
from ccsf_con import googleApiCon as googleApiCon

TEST_EMAIL = "test_studentA@mail.ccsf.edu"
TEST_PASSWORD = "ASDF1234"
TEST_FNAME = "Mickey"
TEST_LNAME = "Mouse"
TEST_NEW_OU = "/Students"


@pytest.fixture
def in_googlecon():
    return_val = googleApiCon.GoogleApiCon()
    return return_val


def test_list_users(in_googlecon):
    output = in_googlecon.list_users()

    assert len(output) == 5


def test_create_user(in_googlecon):
    l_userCreated = in_googlecon.create_user(
        TEST_EMAIL, TEST_PASSWORD, TEST_FNAME, TEST_LNAME
    )

    assert l_userCreated["orgUnitPath"] == "/Prereg-Students"


def test_get_user(in_googlecon):
    l_userFound = in_googlecon.get_user(TEST_EMAIL)

    assert l_userFound["name"]["givenName"] == TEST_FNAME


def test_get_last_login_date(in_googlecon):
    assert in_googlecon.get_last_login_date(TEST_EMAIL) == "1970-01-01T00:00:00.000Z"


def test_get_user_ouPath(in_googlecon):
    l_ouPathFound = in_googlecon.get_user_ouPath(TEST_EMAIL)

    assert l_ouPathFound == "/Prereg-Students"


def test_update_user_password(in_googlecon):
    try:
        in_googlecon.update_user_password(TEST_EMAIL, "JKLM5678")
    except Exception as e:
        assert False, f"'change_user_password' raised exception {e}'"


def test_update_user_ouPath(in_googlecon):
    try:
        in_googlecon.update_user_ouPath(TEST_EMAIL, TEST_NEW_OU)
    except Exception as e:
        assert False, f"'update_user_ou()' raised exception {e}'"


def test_delete_user(in_googlecon):
    try:
        in_googlecon.delete_user(TEST_EMAIL)
    except Exception as e:
        assert False, f"'delete_user()' raised exception {e}'"