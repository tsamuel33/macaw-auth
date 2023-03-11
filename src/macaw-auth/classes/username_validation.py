from .errors import InvalidUsernameError

class UsernameValidation:
    """
    A class to check the validity of a provided username

    ...

    Attributes
    ----------
    username : str
        username for validation
    username_is_email : bool
        determines if the username is expected to be an email address
    symbol_list : list
        list of valid symbols that can be included in username
    validity : bool
        boolean stating if provided username is valid
    """

    # Class variables
    valid_email_symbols = ['_', '-', '.', '@', '+']
    valid_iam_user_symbols = ['+', '=', ',', '.', '@', '_', '-']

    def __init__(self, username: str, username_is_email: bool = True):
        self.username = username
        self.username_is_email = username_is_email
        if self.username_is_email:
            self.symbol_list = self.valid_email_symbols
            self._prefix = self.split_username()[0]
            self._domain = self.split_username()[1]
        else:
            self.symbol_list = self.valid_iam_user_symbols
            self._prefix = self.username
            self._domain = ""
        self.validity = self.check_all()

    # Split username into prefix and domain(only applies to email)
    def split_username(self):
        username_parts = self.username.split('@')
        prefix = username_parts[0]
        if len(username_parts) == 2:
            domain = username_parts[1]
        else:
            domain = ""
        return prefix, domain

    # Helper function to remove specified valid symbols from a string and test
    # if the resulting string is alphanumeric.
    def strip_valid_symbols(self, test_string):
        output = test_string
        for symbol in self.symbol_list:
            output = output.replace(symbol, '')
        output_alphanum = output.isalnum()
        return output, output_alphanum

    # Check if username has invalid symbols
    def check_invalid_symbols(self):
        validity = True
        message = "Provided username contains valid symbols"
        stripped_prefix = self.strip_valid_symbols(self._prefix)
        if not stripped_prefix[1]:
            validity = False
            message = "Provided username contains invalid symbol(s). " + \
                "Provided username can only contain {}".format(
                    ', '.join(self.symbol_list))
            raise InvalidUsernameError(message)
        elif self.username_is_email:
            stripped_domain = self.strip_valid_symbols(self._domain)
            if not stripped_domain[1]:
                validity = False
                message = "The domain of the email address contains " + \
                    "invalid symbol(s). Provided username can only " + \
                    "contain {}".format(', '.join(self.symbol_list))
                raise InvalidUsernameError(message)
        return validity, message

    # Ensure provided email address has a single @ symbol
    def check_single_at(self):
        if self.username_is_email:
            at_count = self.username.count("@")
            if at_count != 1:
                validity = False
                message = "User name should contain a single '@' symbol. " + \
                    "Provided name has {}.".format(at_count)
                raise InvalidUsernameError(message)
            else:
                validity = True
                message = "Email has a single '@' symbol"
        else:
            validity = True
            message = "Username is not an email address. Check not required."
        return validity, message    
    
    # Check if prefix or domain starts with a number or letter
    @staticmethod
    def starts_alphanumeric(test_string, string_type):
        if test_string[0].isalnum():
            validity = True
            message = "{} starts with an alphanumeric character".format(
                string_type)
        else:
            validity = False
            message = "{} does not start with an ".format(string_type) + \
                "alphanumeric character"
            raise InvalidUsernameError(message)
        return validity, message

    # Check if prefix or domain ends with a number or letter
    @staticmethod
    def ends_alphanumeric(test_string, string_type):
        string_length = len(test_string)
        if test_string[string_length-1].isalnum():
            validity = True
            message = "{} ends with an alphanumeric character".format(
                string_type)
        else:
            validity = False
            message = "{} does not end with an ".format(string_type) + \
                "alphanumeric character"
            raise InvalidUsernameError(message)
        return validity, message

    # Check if valid symbols are followed by number or letter
    # Does not check last character as that would cause index error
    @staticmethod
    def is_next_alphanum(test_string):
        validity = True
        if test_string.isalnum():
            pass
        else:
            string_length = len(test_string)
            for x in range(string_length-1):
                if not test_string[x].isalnum():
                    if not test_string[x+1].isalnum():
                        validity = False
                        message = "Username contains consecutive symbols"
                        raise InvalidUsernameError(message)
        if validity:
            message = "Username does not have consecutive symbols"
        return validity, message

    # Check if domain ends in at least 2 characters
    def check_domain_end(self):
        if not self.username_is_email:
            validity = True
            message = "Username is not an email address. Check not required."
        else:
            domain_parts = self._domain.split('.')
            parts_length = len(domain_parts)
            if parts_length < 2:
                validity = False
                message = "Domain contains less than 2 parts separated by '.'"
                raise InvalidUsernameError(message)
            else:
                domain_end = domain_parts[parts_length-1]
                domain_end_length = len(domain_end)
                if not domain_end.isalnum():
                    validity = False
                    message = "Domain ending is not alphanumeric"
                    raise InvalidUsernameError(message)
                elif domain_end_length >= 2:
                    validity = True
                    message = "Domain ends with at least 2 characters"
                else:
                    validity = False
                    message = "Domain ends with less than 2 characters"
                    raise InvalidUsernameError(message)
        return validity, message
    
    # Run all checks and output the validity
    def check_all(self):
        try:
            self.check_single_at()
            self.check_invalid_symbols()
            self.starts_alphanumeric(self._prefix, "Username")
            self.ends_alphanumeric(self._prefix, "Username")
            self.is_next_alphanum(self._prefix)
            if self.username_is_email:
                self.starts_alphanumeric(self._domain, "Domain")
                self.ends_alphanumeric(self._domain, "Domain")
                self.is_next_alphanum(self._domain)
                self.check_domain_end()
            valid_username = True
        except InvalidUsernameError as err:
            valid_username = False
            print('Error: ' + str(err))
        return valid_username