# from . import errors
# Keyring may require importing dbus-python to work on Linux
# dbus-python may not install properly via pip, so may need to disable keyring on linux
import keyring
from getpass import getpass

class UserCredentials:
    """
    A class to represent a user's credentials for authenticating to AWS

    ...

    Attributes
    ----------
    username : str
        username for authentication
    enable_keyring : bool
        boolean determining if keyring should be used to save password
    reset_password : bool
        determines if saved password should be overwritten
    password_stored : bool
        boolean stating if the user's password is saved in keyring
    """

    # Set constant values
    keyring_service_name = "AWSUserCredentials"

    def __init__(self, username, reset_password=False, enable_keyring=False):
        self.username = username
        self.reset_password = reset_password
        self.enable_keyring = enable_keyring
        if enable_keyring:
            keyring.get_keyring()
            self._password_stored = self.check_if_password_stored()
            if not self._password_stored:
                self.set_keyring_password(getpass())
            elif self._password_stored and self.reset_password:
                print('Resetting password.')
                self.set_keyring_password(getpass())
        else:
            self.__password = getpass()
            #TODO - add a way to pass password if keyring is disabled

    def get_keyring_password(self):
        if self.enable_keyring:
            print('Getting password from keyring...')
            creds = keyring.get_password(
                self.keyring_service_name, self.username)
            return creds

    def check_if_password_stored(self):
        result = self.get_keyring_password()
        if result is None:
            print('Password not found.')
            password_stored = False
        else:
            print('Stored password found.')
            password_stored = True
        return password_stored

    def set_keyring_password(self, password):
        if self.enable_keyring:
            keyring.set_password(
                self.keyring_service_name, self.username, password)