# %%
import json
import time
import oracledb
import pandas as pd
from pathlib import Path
from cryptography.fernet import Fernet
from codetiming import Timer
from ccsf_con import get_login
# Global variables
DB_OCI_CONNECTIONS_FILE = '.DbConnections.json'
DB_JSON_FILE_VER_SUPPORTED = "1.01"


class OracleCloudDB:
    """
    A class to manage Oracle Cloud database operations, including connecting to the database,
    executing SQL queries, and closing the connection.

    This class requires Oracle client libraries to be installed on the host that initiates
    the connection. For more details, refer to the Oracle documentation:
    - Instant Client: https://www.oracle.com/database/technologies/instant-client.html
    - Python oracledb module: https://www.oracle.com/database/technologies/appdev/python/quickstartpython.html
    - Installation guide: https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html

    """

    def __init__(self):
        """
        Initialize the OracleCloudDB class without any connection parameters.
        Connection parameters will be provided in the connect() method.
        """
        self.dsn = None
        self.username = None
        self.password = None
        self.connection = None

    def _decrypt_password(self, encrypted_password, crytokey):
        """
        Decrypt the password using the provided cryptographic key.

        Parameters:
        encrypted_password (str): The encrypted password.
        crytokey (str): The key used for decryption.

        Returns:
        str: The decrypted password.

        Raises:
        ValueError: If the decryption fails.
        """
        try:
            fernet = Fernet(crytokey.encode())
            decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
            return decrypted_password
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def connect(self, connection_name, retries=3, delay=5):
        """
        Establish a connection to the Oracle Cloud database using parameters from a JSON file.

        This method searches for the DB_OCI_CONNECTIONS_FILE file in the current directory,
        and if not found, in the user's home directory. If the file is not found in either
        location, a FileNotFoundError is raised.

        Parameters:
        connection_name (str): The name of the connection to use from the DB_OCI_CONNECTIONS_FILE file.
        retries (int, optional): The number of retry attempts. Default is 3.
        delay (int, optional): The delay in seconds between retry attempts. Default is 5 seconds.

        Raises:
        FileNotFoundError: If the DB_OCI_CONNECTIONS_FILE file is not found in the current or home directory.
        ValueError: If the specified connection name is not found in the JSON file.
        ValueError: If the version of the JSON file is not supported by the class.
        oracledb.DatabaseError: If a database connection error occurs and the retries are exhausted.
        """
        config = get_login(DB_OCI_CONNECTIONS_FILE, DB_JSON_FILE_VER_SUPPORTED)

        if 'instclientpath' in config:
            oracledb.init_oracle_client(lib_dir=config['instclientpath'])
            print(f"Oracle client initialized with libraries from: {config['instclientpath']}")

        conn_df = pd.DataFrame.from_dict(config.get('connections'), orient="columns")

        # Find the connection details by name
        l_filter = conn_df.name == connection_name
        conn_df = conn_df[l_filter]
        conn_details = conn_df['info'].values[0]

        if not conn_details:
            raise ValueError(f"Connection '{connection_name}' not found in {json_file_path}")

        # Decrypt the password using the cryptographic key if available
        crytokey = conn_details.get('crytokey')
        if crytokey:
            encrypted_password = conn_details['password']
            self.password = self._decrypt_password(encrypted_password, crytokey)
            print("Using decrypted password from JSON file.")
        else:
            self.password = conn_details['password']
            print("Using plain password from JSON file.")

        # Construct the DSN (Data Source Name) for the connection
        self.dsn = oracledb.makedsn(host=conn_details['hostname'], port=conn_details['port'],
                                    service_name=conn_details['serviceName'])
        self.username = conn_details['user']

        # Attempt to connect with retry logic
        for attempt in range(retries):
            try:
                self.connection = oracledb.connect(
                    user=self.username,
                    password=self.password,
                    dsn=self.dsn
                )

                print(f"Successfully connected to Oracle Cloud database '{connection_name}'")
                return  # Exit the function if connection is successful
            except oracledb.DatabaseError as e:
                if attempt < retries - 1:
                    print(f"Error connecting to Oracle Cloud database: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to connect after {retries} attempts.")
                    raise
    @Timer()
    def execute_sql(self, sql, params=None):
        """
        Execute an arbitrary SQL query in the connected Oracle Cloud database.

        Parameters:
        sql (str): The SQL query to execute.
        params (tuple, optional): The parameters to bind to the SQL query.

        Returns:
        DataFrame or None: A DataFrame containing the fetched rows if the query is a SELECT statement; otherwise, None.

        Raises:
        oracledb.DatabaseError: If an error occurs during SQL execution.
        """
        try:
            l_cursor = self.connection.cursor()
            l_cursor.execute(sql, params or ())
            if l_cursor.description:  # This checks if the statement is a SELECT
                columns = [col[0] for col in l_cursor.description]
                result = pd.DataFrame(l_cursor.fetchall(), columns=columns)
                return result
            else:
                self.connection.commit()
                # print(f"SQL executed: {sql}")
        except oracledb.DatabaseError as e:
            raise
        finally:
            l_cursor.close()

    def close_connection(self):
        """
        Close the connection to the Oracle Cloud database.

        Raises:
        oracledb.DatabaseError: If an error occurs during the closing of the connection.
        """
        if self.connection:
            try:
                self.connection.close()
                print("Database connection closed.")
            except oracledb.DatabaseError as e:
                raise
