from src.macaw_auth.classes.user_credentials import UserCredentials

class TestCredentials:

    def test_login(self):
        name = UserCredentials("email@domain.com", False, False)