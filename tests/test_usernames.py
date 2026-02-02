from src.macaw_auth.classes.username_validation import UsernameValidation
from src.macaw_auth.classes.username_validation import InvalidUsernameError
import pytest

class TestUsernameValidation:

    @staticmethod
    def validate_user(
            username : str,
            expect_pass : bool = True,
            error_regex : str = None
            ) -> None:
        with pytest.raises(InvalidUsernameError, match=error_regex):
            try:
                UsernameValidation(username)
                if not expect_pass:
                    pytest.fail("Expected InvalidUsernameError was not raised")
            except InvalidUsernameError as e:
                if expect_pass:
                    pytest.fail(f"Unexpected InvalidUsernameError raised: {e.message}")
                else:
                    pass

    # Email Tests
    def test_valid_email(self):
        self.validate_user("fake@example.com")

    def test_invalid_email_symbols(self):
        self.validate_user("user@equ=als.edu", False, "contains invalid symbol")

    def test_invalid_email_multiple_ats(self):
        self.validate_user("user@hello@fake.com", False, "User name should contain a single '@' symbol")

    def test_invalid_email_non_alphanum_start_prefix(self):
        self.validate_user(".invalid@hello.net", False, "does not start with an alphanumeric character")

    def test_invalid_email_non_alphanum_start_domain(self):
        self.validate_user("notright@+ultra.ua", False, "does not start with an alphanumeric character")

    def test_invalid_email_non_alphanum_end_prefix(self):
        self.validate_user("invalid+@hello.net", False, "does not end with an alphanumeric character")

    def test_invalid_email_non_alphanum_end_domain(self):
        self.validate_user("notright@ultra.ua+", False, "does not end with an alphanumeric character")

    def test_invalid_email_alphanum_after_symbol(self):
        self.validate_user("hello@dot.+com", False, "Username contains consecutive symbols")

    def test_invalid_email_short_domain(self):
        self.validate_user("short@xy.z", False, "less than 2")

    # User Tests
    def test_valid_user(self):
        self.expect_valid_result("fakeusername")

    def test_invalid_user_invalid_symbol(self):
        self.validate_user("user1!", False, "contains invalid symbol")

    def test_invalid_user_alphanum_after_symbol(self):
        self.validate_user("invalid+=user", False, "Username contains consecutive symbols")