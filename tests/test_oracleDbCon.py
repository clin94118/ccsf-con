# %%
import pytest
from ccsf_con import oracleDbCon as oracleDbCon


@pytest.fixture
def in_inst():
    return "OCI_PPRD"


@pytest.fixture
def in_dbcon(in_inst):

    return_val = oracleDbCon.OracleCloudDB()
    return_val.connect(in_inst)
    return return_val


def test_crypto():
    assert 1 == 1


def test_connect_query(in_dbcon):

    my_sql = """
        select * from spriden where spriden_id = :id
    """
    output = in_dbcon.execute_sql(my_sql, dict(id="@00287808"))
    assert output["SPRIDEN_PIDM"][0] == 1165006


def test_close_connection(in_dbcon):
    try:
        in_dbcon.close_connection()
    except Exception as err:
        pytest.fail(f"Connection Close failed: {err}")
