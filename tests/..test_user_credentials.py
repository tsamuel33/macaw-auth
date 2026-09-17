from src.macaw_auth.classes.user_credentials import UserCredentials


class TestCredentials:
    def test_login(self):
        UserCredentials("email@domain.com", False, False)
