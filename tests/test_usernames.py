from src.macaw_auth.classes.username_validation import UsernameValidation
from src.macaw_auth.classes.errors import InvalidUsernameError
import pytest

def validate_user(username : str, is_email : bool = True, expected_result : bool = False) -> None:
    user = UsernameValidation(username, is_email)
    if expected_result:
        assert user.validity
    elif not expected_result:
        assert not user.validity

# Email Tests
def test_valid_email():
    validate_user("fake@example.com", expected_result=True)

def test_invalid_email_symbols():
    with pytest.raises(InvalidUsernameError, match="contains invalid symbol"):
        validate_user("user@equ=als.edu")

def test_invalid_email_multiple_ats():
    with pytest.raises(InvalidUsernameError, match="User name should contain a single '@' symbol"):
        validate_user("user@hello@fake.com")

def test_invalid_email_non_alphanum_start_prefix():
    with pytest.raises(InvalidUsernameError, match="does not start with an alphanumeric character"):
        validate_user(".invalid@hello.net")

def test_invalid_email_non_alphanum_start_domain():
    with pytest.raises(InvalidUsernameError, match="does not start with an alphanumeric character"):
        validate_user("notright@+ultra.ua")

def test_invalid_email_non_alphanum_end_prefix():
    with pytest.raises(InvalidUsernameError, match="does not end with an alphanumeric character"):
        validate_user("invalid+@hello.net")

def test_invalid_email_non_alphanum_end_domain():
    with pytest.raises(InvalidUsernameError, match="does not end with an alphanumeric character"):
        validate_user("notright@ultra.ua+")

def test_invalid_email_alphanum_after_symbol():
    with pytest.raises(InvalidUsernameError, match="Username contains consecutive symbols"):
        validate_user("hello@dot.+com")

def test_invalid_email_short_domain():
    with pytest.raises(InvalidUsernameError, match="less than 2"):
        validate_user("short@xy.z")

# User Tests
def test_valid_user():
    validate_user("fakeusername", is_email=False, expected_result=True)

def test_invalid_user_invalid_symbol():
    with pytest.raises(InvalidUsernameError, match="contains invalid symbol"):
        validate_user("user1!", False, False)

def test_invalid_user_alphanum_after_symbol():
    with pytest.raises(InvalidUsernameError, match="Username contains consecutive symbols"):
        validate_user("invalid+=user", False, False)