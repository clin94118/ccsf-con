import time
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ccsf_con import get_login, get_with_default, debug_print, ProcessingError

# Global variables
API_CONNECTIONS_FILE = "api.ini"
API_FILE_VER_SUPPORTED = "0.5"
PREREG_OU = "/Prereg-Students"
STUDENTS_OUPATH = "/Students"
NOREG_OUPATH = "/No-Reg"


class GoogleApiCon:
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
        create_user:          Creates a new user in the domain.
        get_user:             Retrieves details for a single user based on their email.
        get_user_ouPath:      Retrieves the organizational unit path of a user.
        get_last_login_date:  Retrieves the last login date of a user.
        update_user_name:     Update the name of a user.
        update_user_password: Update the password of a user.
        update_user_ouPath:   Update the organizational unit path for a user.
        delete_user:          Deletes a user from the domain.
    """

    def __init__(self):
        conns = get_login(API_CONNECTIONS_FILE, API_FILE_VER_SUPPORTED, "INI")

        self.service_account_file = get_with_default(
            conns, "GOOGLE", "service_account_file"
        )
        self.service_account_email = get_with_default(
            conns, "GOOGLE", "service_account_email"
        )
        scopes = get_with_default(conns, "GOOGLE", "default_scope")
        self.scopes = scopes.split(",")
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
                service_account_file_path = (
                    Path.home() / ".logins" / self.service_account_file
                )

            creds = service_account.Credentials.from_service_account_file(
                service_account_file_path,
                scopes=self.scopes,
                subject=self.service_account_email,
            )
            return build("admin", "directory_v1", credentials=creds)

        except Exception as e:
            raise ProcessingError(
                "Authentication failed during API setup", reason=str(e)
            )

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
                        "primaryEmail": user["primaryEmail"],
                        "fullName": user["name"]["fullName"],
                    }

                    debug_print(
                        f"      {user['primaryEmail']} ({user['name']['fullName']})"
                    )
                    user_list.append(user_details)

            return user_list  # Return the list of users
        except HttpError as e:
            raise ProcessingError(
                "Error listing users", status_code=e.resp.status, reason=e.reason
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during user listing", reason=str(e)
            )

    def create_user(
        self,
        email,
        password,
        first_name,
        last_name,
        org_unit_path=PREREG_OU,
        max_wait_time=5,
    ):
        """
        Creates a new user in the domain and waits for the user to be successfully created.

        Args:
            email (str): The email address for the new user.
            password (str): The password for the new user.
            first_name (str): The first name of the new user.
            last_name (str): The last name of the new user.
            org_unit_path (str, optional): The organizational unit path to assign the user. Defaults to "/Prereg-Students".
            max_wait_time (int, optional): The maximum wait time in seconds before giving up. Defaults to 5 seconds.

        Returns:
            dict: The user's details in JSON format.

        Raises:
            GoogleProcessingError: If there is an error during the user creation process or if the user is not created within the maximum wait time.
        """

        debug_print(
            f"\nAttempting to insert new user {email} with password: {password}\n"
        )

        new_user = {
            "primaryEmail": email,
            "orgUnitPath": org_unit_path,
            "password": password,
            "name": {"givenName": first_name, "familyName": last_name},
            "changePasswordAtNextLogin": False,
        }

        # Attempt to create the user
        try:
            results = self.service.users().insert(body=new_user).execute()

            primary_email = results.get("primaryEmail", [])
            creation_time = results.get("creationTime", [])
            debug_print(
                f"    {primary_email}\n    created with password: {password} at {creation_time}"
            )

            # Now, check every second if the user is successfully created
            wait_time = 0
            while wait_time < max_wait_time:
                # Get the user details again to see if it's created
                try:
                    user_check = self.service.users().get(userKey=email).execute()
                    # If user details are retrieved, the user is created
                    debug_print(
                        f"    User {email} successfully created within {wait_time} seconds."
                    )
                    return user_check  # Return the user details

                except HttpError:
                    # If user not found, wait for 1 second and retry
                    time.sleep(1)
                    wait_time += 1
                    debug_print(f"    Waited {wait_time} seconds, checking again...")

            # If the user is not created within the max_wait_time, raise an exception
            raise ProcessingError(
                f"User {email} creation timed out after {max_wait_time} seconds."
            )

        except ProcessingError as e:
            raise e
        except HttpError as e:
            raise ProcessingError(
                "Error creating user", status_code=e.resp.status, reason=e.reason
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during user creation", reason=str(e)
            )

    def get_user(self, email):
        """
        Retrieves details for a specific user based on their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            dict: The user's details in JSON format.

        Raises:
            ProcessingError: If there is an error during the user retrieval process.
        """

        debug_print(f"\nAttempting to get Gmail record for {email}\n")

        try:
            results = self.service.users().get(userKey=email).execute()
            name = results.get("name", {}).get("fullName", "N/A")
            last_login_time = results.get("lastLoginTime", "N/A")
            org_unit_path = results.get("orgUnitPath", "N/A")
            debug_print(
                f"    {name} last logged in as {email}\n    at UTC time {last_login_time}"
            )
            debug_print(f"    Current OUPATH: {org_unit_path}")
            return results

        except HttpError as e:
            raise ProcessingError(
                "Error getting user", status_code=e.resp.status, reason=e.reason
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during user retrieval", reason=str(e)
            )

    def get_user_ouPath(self, email):
        """
        Retrieves the organizational unit (OU) path of a user.

        Args:
            email (str): The email address of the user.

        Returns:
            str: The OU path of the user.

        Raises:
            GoogleProcessingError: If there is an error during the retrieval process.
        """

        debug_print(f"\nAttempting to get OU path for user {email} \n")

        try:
            user_details = self.service.users().get(userKey=email).execute()
            ou_path = user_details.get("orgUnitPath")
            debug_print(f"    OU path for user {email}: {ou_path}")
            return ou_path

        except HttpError as e:
            raise ProcessingError(
                "Error retrieving user OU path",
                status_code=e.resp.status,
                reason=e.reason,
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during OU path retrieval", reason=str(e)
            )

    def get_last_login_date(self, email):
        """
        Retrieves the last login date of a user.

        Args:
            email (str): The email address of the user.

        Returns:
            str: The last login date of the user in ISO 8601 format.

        Raises:
            GoogleProcessingError: If there is an error during the retrieval process.
        """

        debug_print(f"\nAttempting to get last login date for user {email} \n")

        try:
            user_details = self.service.users().get(userKey=email).execute()
            last_login_time = user_details.get("lastLoginTime")
            debug_print(f"    Last login time for user {email}: {last_login_time}")
            return last_login_time

        except HttpError as e:
            raise ProcessingError(
                "Error retrieving user last login date",
                status_code=e.resp.status,
                reason=e.reason,
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during last login retrieval", reason=str(e)
            )

    def update_user_name(self, email, new_given_name, new_family_name):
        """
        Changes the name of a user.

        Args:
            email (str): The email address of the user whose name is being changed.
            new_given_name (str): The new given name to set.
            new_family_name (str): The new family name to set.

        Raises:
            GoogleProcessingError: If there is an error during the name change process.
        """

        debug_print(f"\nAttempting to change name for user {email} \n")

        try:
            user_data = {
                "name": {"givenName": new_given_name, "familyName": new_family_name}
            }
            self.service.users().update(userKey=email, body=user_data).execute()
            debug_print(f"    Name for user {email} changed successfully.")

        except HttpError as e:
            raise ProcessingError(
                "Error changing user name", status_code=e.resp.status, reason=e.reason
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during name change", reason=str(e)
            )

    def update_user_password(self, email, new_password):
        """
        Changes the password of a user.

        Args:
            email (str): The email address of the user whose password is being changed.
            new_password (str): The new password to set.

        Raises:
            GoogleProcessingError: If there is an error during the password change process.
        """

        debug_print(f"\nAttempting to change password for user {email} \n")

        try:
            user_data = {"password": new_password}
            self.service.users().update(userKey=email, body=user_data).execute()
            debug_print(f"    Password for user {email} changed successfully.")

        except HttpError as e:
            raise ProcessingError(
                "Error changing user password",
                status_code=e.resp.status,
                reason=e.reason,
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during password change", reason=str(e)
            )

    def update_user_ouPath(self, email, new_ou):
        """
        Updates the organizational unit (OU) path for a specific user.

        Args:
            email (str): The email address of the user to update.
            new_ou (str): The new organizational unit path to assign to the user.

        Raises:
            GoogleProcessingError: If there is an error during the user update process.
        """

        debug_print(f"\nAttempting to switch OU path for {email} to {new_ou}\n")

        update_user = {"orgUnitPath": new_ou}

        try:
            results = (
                self.service.users().update(userKey=email, body=update_user).execute()
            )
            primary_email = results.get("primaryEmail", [])
            ou_path = results.get("orgUnitPath", [])
            debug_print(f"    {primary_email} updated OUPATH: {ou_path}")

        except HttpError as e:
            raise ProcessingError(
                "Error updating user OU", status_code=e.resp.status, reason=e.reason
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during user OU update", reason=str(e)
            )

    def delete_user(self, email, max_wait_time=60, check_interval=1):
        """
        Deletes a user by their email address and waits for the deletion to complete.

        Args:
            email (str): The email address of the user to delete.
            max_wait_time (int): Maximum wait time in seconds to check if the user is deleted (default is 10 seconds).
            check_interval (int): Interval between checks in seconds (default is 1 second).

        Raises:
            GoogleProcessingError: If there is an error during the deletion process.
        """
        debug_print(f"\nAttempting to delete a user {email} \n")

        try:
            # First, attempt to delete the user
            results = self.service.users().delete(userKey=email).execute()
            debug_print(
                f"    User {email} deletion initiated. Waiting for confirmation..."
            )

            # Wait for the user to be successfully deleted
            wait_time = 0
            while wait_time < max_wait_time:
                try:
                    # Attempt to get the user, which will fail if the user is deleted
                    self.service.users().get(userKey=email).execute()

                except HttpError as e:
                    if (
                        e.resp.status == 404
                    ):  # User not found means deletion is successful
                        debug_print(
                            f"    User {email} deleted successfully within {wait_time} seconds."
                        )
                        return  # Exit as user has been deleted

                time.sleep(check_interval)
                wait_time += check_interval
                debug_print(f"    Waited {wait_time} seconds, checking again...")

            # If we exceed the max wait time, raise an error
            raise ProcessingError(
                f"User {email} deletion did not complete within {max_wait_time} seconds."
            )

        except ProcessingError as e:
            raise e
        except HttpError as e:
            raise ProcessingError(
                "Error deleting user", status_code=e.resp.status, reason=e.reason
            )
        except Exception as e:
            raise ProcessingError(
                "An unknown error occurred during user deletion", reason=str(e)
            )
