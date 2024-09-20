# %%
import pytest
from ccsf_con import oracleDbCon as oracleDbCon

@pytest.fixture
def in_inst():
    return "OCI_PPRD"

def test_connect_query(in_inst):
    my_db = oracleDbCon.OracleCloudDB()
    my_db.connect(in_inst)

    my_sql = """
        select * from spriden where spriden_id = :id
    """
    output = my_db.execute_sql(my_sql, dict(id='@00287808'))
    assert output['SPRIDEN_PIDM'][0] == 1165006

def test_close_connection(in_inst):
    try:
        my_db = oracleDbCon.OracleCloudDB()
        my_db.connect(in_inst)

        my_db.close_connection()
    except Exception as err:
        pytest.fail(f"Connection Close failed: {err}");
