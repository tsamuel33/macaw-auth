class InvalidUsernameError(Exception):
    """Raises an exception when an invalid username is entered

    Attributes:
        message -- message indicating the specifics of the error
    """

    def __init__(self, message='Invalid user name entered'):
        self.message = message
        super().__init__(self.message)


class ConfigurationError(Exception):
    """Raises an exception when required configuration items are
    set incorrectly.

    Attributes:
        message -- message indicating the specifics of the error
    """

    def __init__(self,
            message='Incorrect configuration. Check your configuration file'):
        self.message = message
        super().__init__(self.message)