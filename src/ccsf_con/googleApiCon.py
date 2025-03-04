import time
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ccsf_con import get_login, get_with_default, debug_print, ProcessingError

# Global variables
API_CONNECTIONS_FILE = "api.ini"
API_FILE_VER_SUPPORTED = "0.5"

class googleApiCon:
    """
    A class to interact with the Google Admin Directory API using a service account.

    This class facilitates interactions with the Google Admin API for managing users,
    their organizational unit (OU) paths, and other user-related operations such as
    listing, creating, updating, and deleting users.

    Attributes:
        service_account_file (str): The path to the service account JSON file.
        service_account_email (str): The email address of the service account.
        scopes (list): A list of OAuth 2.0 scopes needed for the API calls.
        service (Resource): The authenticated Google API service object for the Admin API.

    Methods:
        authenticate:         Authenticates with the Google Admin API using the service account.
        list_users:           Retrieve list users in the domain.
        get_user:             Retrieves details for a single user based on their email.
        get_user_ou_path:     Retrieves the organizational unit path of a user.
        get_last_login_date:  Retrieves the last login date of a user.
        create_user:          Creates a new user in the domain.
        delete_user:          Deletes a user from the domain.
        update_user_name:     Update the name of a user.
        update_user_ou:       Update the organizational unit path for a user.
        update_user_password: Update the password of a user.
    """
    def __init__(self, ):
        conns = get_login(API_CONNECTIONS_FILE, API_FILE_VER_SUPPORTED, "INI")

        self.service_account_file = get_with_default(conns, "GOOGLE", "service_account_file")
        self.service_account_email = get_with_default(conns, "GOOGLE", "service_account_email")
        scopes = get_with_default(conns, "GOOGLE", "default_scope")
        self.scopes = scopes.split(',')
        self.service = self.authenticate()

    def authenticate(self):
        """
        Authenticates the service account with Google Admin API using the provided credentials.

        Returns:
            googleapiclient.discovery.Resource: The authenticated service object to interact with Google APIs.

        Raises:
            ProcessingError: If there is an error during the authentication process.
        """
        try:

            service_account_file_path = Path.cwd() / self.service_account_file

            if not service_account_file_path.is_file():
                service_account_file_path = Path.home() / ".logins" / self.service_account_file

            creds = service_account.Credentials.from_service_account_file(
                service_account_file_path,
                scopes=self.scopes,
                subject=self.service_account_email
            )
            return build("admin", "directory_v1", credentials=creds)

        except Exception as e:
            raise ProcessingError("Authentication failed during API setup", reason=str(e))

    def list_users(self, num_records=5):
        """
        return list of users in the domain.

        Args:
            num_records (int): The number of users to list (default is 5).

        Returns:
            list: A list of dictionaries containing user details with their primary email and full name.

        Raises:
            ProcessingError: If there is an error during the listing process.
        """
        debug_print(f"\nGetting the first {num_records} users in the domain\n")
        try:
            results = (
                self.service.users()
                .list(customer="my_customer", maxResults=num_records, orderBy="email")
                .execute()
            )

            users = results.get("users", [])
            user_list = []

            if not users:
                debug_print("No users in the domain.")
            else:
                debug_print(f"      Returning {len(user_list)} users.")

                for user in users:
                    user_details = {
                        "primaryEmail": user['primaryEmail'],
                        "fullName": user['name']['fullName']
                    }

                    debug_print(f"      {user['primaryEmail']} ({user['name']['fullName']})")
                    user_list.append(user_details)

            return user_list  # Return the list of users
        except HttpError as e:
            raise ProcessingError("Error listing users", status_code=e.resp.status, reason=e.reason)
        except Exception as e:
            raise ProcessingError("An unknown error occurred during user listing", reason=str(e))
