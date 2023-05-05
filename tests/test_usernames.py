from src.macaw_auth.classes.username_validation import UsernameValidation
from src.macaw_auth.classes.errors import InvalidUsernameError
import pytest

class TestUsernameValidation:

    @staticmethod
    def validate_user(
            username : str,
            is_email : bool = True, # Most tests are email addresses
            expected_result : bool = False # Most tests are exceptions
            ) -> None:
        user = UsernameValidation(username, is_email)
        if expected_result:
            assert user.validity
        elif not expected_result:
            assert not user.validity

    def expect_valid_result(self, username : str, is_email : bool = True) -> None:
        self.validate_user(username, is_email, expected_result=True)

    def expect_exception(self, username : str, is_email : bool, exception_regex : str) -> None:
        with pytest.raises(InvalidUsernameError, match=exception_regex):
            self.validate_user(username, is_email, expected_result=False)

    # Email Tests
    def test_valid_email(self):
        self.expect_valid_result("fake@example.com")

    def test_invalid_email_symbols(self):
        self.expect_exception("user@equ=als.edu", True,  "contains invalid symbol")

    def test_invalid_email_multiple_ats(self):
        self.expect_exception("user@hello@fake.com", True,  "User name should contain a single '@' symbol")

    def test_invalid_email_non_alphanum_start_prefix(self):
        self.expect_exception(".invalid@hello.net", True, "does not start with an alphanumeric character")

    def test_invalid_email_non_alphanum_start_domain(self):
        self.expect_exception("notright@+ultra.ua", True, "does not start with an alphanumeric character")

    def test_invalid_email_non_alphanum_end_prefix(self):
        self.expect_exception("invalid+@hello.net", True, "does not end with an alphanumeric character")

    def test_invalid_email_non_alphanum_end_domain(self):
        self.expect_exception("notright@ultra.ua+", True, "does not end with an alphanumeric character")

    def test_invalid_email_alphanum_after_symbol(self):
        self.expect_exception("hello@dot.+com", True, "Username contains consecutive symbols")

    def test_invalid_email_short_domain(self):
        self.expect_exception("short@xy.z", True, "less than 2")

    # # User Tests
    def test_valid_user(self):
        self.expect_valid_result("fakeusername", is_email=False)

    def test_invalid_user_invalid_symbol(self):
        self.expect_exception("user1!", False, "contains invalid symbol")

    def test_invalid_user_alphanum_after_symbol(self):
        self.expect_exception("invalid+=user", False, "Username contains consecutive symbols")