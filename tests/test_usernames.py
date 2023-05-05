from src.macaw_auth.classes.username_validation import UsernameValidation
from src.macaw_auth.classes.errors import InvalidUsernameError
import pytest

def validate_user(username, is_email, expected_result : bool):
    user = UsernameValidation(username, is_email)
    if expected_result:
        assert user.validity
    elif not expected_result:
        assert not user.validity

# Email Tests
def test_valid_email():
    validate_user("fake@example.com", True, True)

def test_invalid_email_symbols():
    # with pytest.raises(InvalidUsernameError, validate_user, "us=er@equals.edu", True, True)
    with pytest.raises(InvalidUsernameError) as err:

        # validate_user("us=er@equals.edu", True, True)
        user = UsernameValidation("us=er@equals.edu", True)
        print(str(err))

def test_invalid_email_multiple_ats():
    validate_user("user@hello@fake.com", True, False)

def test_invalid_email_non_alphanum_start_prefix():
    validate_user(".invalid@hello.net", True, False)

def test_invalid_email_non_alphanum_start_domain():
    validate_user("notright@+ultra.ua", True, False)

def test_invalid_email_non_alphanum_end_prefix():
    validate_user("invalid+@hello.net", True, False)

def test_invalid_email_non_alphanum_end_domain():
    validate_user("notright@ultra.ua+", True, False)

def test_invalid_email_alphanum_after_symbol():
    validate_user("hello@dot.+com", True, False)

def test_invalid_email_short_domain():
    validate_user("short@xy.z", True, False)

# User Tests
def test_valid_user():
    validate_user("fakeusername", False, True)

def test_invalid_user_invalid_symbol():
    validate_user("user1!", False, False)

def test_invalid_user_alphanum_after_symbol():
    validate_user("invalid+=user", False, False)