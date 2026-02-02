class InvalidUsernameError(Exception):
    """
    Raises an exception when an invalid username is entered

    Attributes:
        message (str): Message indicating the specifics of the error
    """

    def __init__(self, message='Invalid user name entered'):
        self.message = message
        super().__init__(self.message)

class UsernameValidation:
    """
    Checks the validity of a provided username

    Attributes:
        username (str): Username for validation
        username_prefix (str): The prefix of the user's email (if
            applicable)
        username_type (str): The type of user (Email or IAM)
        user_domain (str): The user's email domain (if applicable)
        valid_symbol_list (list): List of valid symbols that can be
            included in username
    """

    valid_email_symbols = ['_', '-', '.', '@', '+']
    valid_iam_user_symbols = ['+', '=', ',', '.', '@', '_', '-']

    def __init__(self, username: str):
        """
        Constructs the attributes of the UsernameValidation object
        
        Arguments:
            username (str): Username for validation
        """

        self.username = username
        self._user_attributes = self.split_username()
        self.username_prefix = self._user_attributes[0]
        self.username_type = self._user_attributes[1]
        self.user_domain = self._user_attributes[2]
        if self.username_type == "email":
            self.valid_symbol_list = self.valid_email_symbols
        else:
            self.valid_symbol_list = self.valid_iam_user_symbols
        self._symbols_string = ', '.join(self.valid_symbol_list)
        self.check_all()

    def split_username(self):
        """
        Determines username type and splits into prefix and domain if
        username is an email address
        
        Returns:
            prefix (str): The first part of the username
            user_type (str): The type of username
            domain (str): The domain of the user if an email address
        """

        user_type = "iam"
        username_parts = self.username.split('@')
        prefix = username_parts[0]
        if len(username_parts) == 2:
            domain = username_parts[1]
            user_type = "email"
        else:
            domain = ""
        return prefix, user_type, domain

    def check_invalid_symbols(self):
        """
        Tests a username to ensure that all characters are alphanumeric
        after valid special characters are removed
        """

        clean_username = self.username
        for symbol in self.valid_symbol_list:
            clean_username = clean_username.replace(symbol, '')
        if not clean_username.isalnum():
            message = "Provided username contains invalid symbol(s)." \
                      " Provided username can only contain" \
                      f"{self._symbols_string}"
            raise InvalidUsernameError(message)

    def check_single_at(self):
        """
        Validates that email address only contains a single '@' symbol
        """

        if self.username_type == "email":
            at_count = self.username.count("@")
            if at_count != 1:
                message = "User name should contain a single '@' " \
                          f"symbol. Provided name has {at_count}."
                raise InvalidUsernameError(message)
    
    def starts_alphanumeric(self, entry : str, entry_type : str):
        """
        Tests if provided string begins with an alphanumeric character
        
        Arguments:
            entry (str): The string to test
            entry_type (str): The type of string (Username or Domain)
        """

        if not entry[0].isalnum():
            message = f"{entry_type} does not start with an " \
                      "alphanumeric character"
            raise InvalidUsernameError(message)

    def ends_alphanumeric(self, entry : str, entry_type :  str):
        """
        Tests if provided string ends with an alphanumeric character
        
        Arguments:
            entry (str): The string to test
            entry_type (str): The type of string (Username or Domain)
        """

        string_length = len(entry)
        if not entry[string_length-1].isalnum():
            message = f"{entry_type} does not end with an " \
                "alphanumeric character"
            raise InvalidUsernameError(message)

    def is_next_alphanum(self, entry : str):
        """
        Test to ensure that username does not contain consecutive
        symbols

        Arguments:
            entry (str): The string to test
        """

        if not entry.isalnum():
            string_length = len(entry)
            for x in range(string_length-1):
                if not entry[x].isalnum():
                    if not entry[x+1].isalnum():
                        message = "Username contains consecutive " \
                                  "symbols"
                        raise InvalidUsernameError(message)

    def check_domain_end(self):
        """
        Tests if username's domain ends in at least 2 characters if the
        username is an email address
        """

        if self.username_type == "email":
            domain_parts = self._domain.split('.')
            parts_length = len(domain_parts)
            if parts_length < 2:
                message = "Domain contains less than 2 parts " \
                          "separated by '.'"
                raise InvalidUsernameError(message)
            else:
                domain_end = domain_parts[parts_length-1]
                domain_end_length = len(domain_end)
                if not domain_end.isalnum():
                    message = "Domain ending is not alphanumeric"
                    raise InvalidUsernameError(message)
                elif domain_end_length < 2:
                    message = "Domain ends with less than 2 characters"
                    raise InvalidUsernameError(message)
    
    def check_all(self):
        """
        Runs all defined validation methods to ensure that the username
        is valid
        """

        self.check_single_at()
        self.check_invalid_symbols()
        self.starts_alphanumeric(self._prefix, "Username")
        self.ends_alphanumeric(self._prefix, "Username")
        self.is_next_alphanum(self._prefix)
        if self.username_type == "email":
            self.starts_alphanumeric(self._domain, "Domain")
            self.ends_alphanumeric(self._domain, "Domain")
            self.is_next_alphanum(self._domain)
            self.check_domain_end()