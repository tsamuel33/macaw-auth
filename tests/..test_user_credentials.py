from src.macaw_auth.classes.user_credentials import UserCredentials

def test_login():
    name = UserCredentials("email@domain.com", False, False)