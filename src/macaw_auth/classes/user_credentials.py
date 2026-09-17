# from . import errors
# Keyring may require importing dbus-python to work on Linux
# dbus-python may not install properly via pip; maybe disable keyring on Linux
from getpass import getpass

import keyring

from macaw_auth.classes.idp_connection import SAMLAssertion


class UserCredentials:
    """
    Represents a user's credentials for authenticating to AWS

    Attributes
        keyring_service_name (str): Name of the service within keyring that
            stores the user's credentials. Set to "AWSUserCredentials".
        username (str): username for authentication
        enable_keyring (bool): boolean determining if keyring should be used
            to save password
        assertion (SAMLAssertion): SAML assertion details after login attempt
    """

    keyring_service_name = "AWSUserCredentials"

    def __init__(
        self,
        username: str,
        identity_url,
        auth_type,
        ssl_verification=True,
        reset_password=False,
        enable_keyring=False,
    ):
        """
        Construct the attributes of the UserCredentials object

        Attributes:
            username (str): user's login name
            identity_url (str): url used to log in to AWS
            auth_type (str): whether authentication is via web form or ntlm
            ssl_verification (bool): verify identity URL's SSL certificate
            reset_password (bool): determines if saved password should be
                overwritten
            enable_keyring (bool): determines if password is retrieved from
                keyring
        """
        self.username = username
        self.enable_keyring = enable_keyring
        if enable_keyring.lower() == "true":
            keyring.get_keyring()
            self._password_stored = self.check_if_password_stored()
            if not self._password_stored:
                self.set_keyring_password(getpass())
            elif self._password_stored and reset_password:
                print("Resetting password.")
                self.set_keyring_password(getpass())
            self.__password = self.get_keyring_password()
        else:
            self.__password = getpass()
        self.assertion = SAMLAssertion(
            self.username,
            self.__password,
            identity_url,
            auth_type,
            ssl_verification,
        ).assertion

    def get_keyring_password(self):
        """
        Retrieve's password from keyring

        """
        if self.enable_keyring:
            print("Getting password from keyring...")
            creds = keyring.get_password(
                self.keyring_service_name, self.username
            )
            return creds

    def check_if_password_stored(self):
        """
        Check's if user's password is stored in keyring

        Returns:
            password_stored (bool): whether or not the password is stored in
                keyring
        """
        result = self.get_keyring_password()
        if result is None:
            print("Password not found.")
            password_stored = False
        else:
            print("Stored password found.")
            password_stored = True
        return password_stored

    def set_keyring_password(self, password):
        """
        Sets password within keyring
        """
        if self.enable_keyring:
            keyring.set_password(
                self.keyring_service_name, self.username, password
            )
