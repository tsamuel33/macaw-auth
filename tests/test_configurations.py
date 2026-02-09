from pathlib import Path

import pytest

from src.macaw_auth.classes.configuration import Configuration
from src.macaw_auth.classes.configuration import ConfigurationError

class TestConfigurationFiles:

    config_file = Path.cwd() / "tests" / "test_files" / "config"
    creds_file = Path.cwd() / "tests" / "test_files" / "credentials"

    def test_use_default_values(self):
        config = Configuration("use-defaults", self.config_file)
        idp = config.get_config_setting("idp_name")
        assert idp == "ADFS"

    def test_account_num(self):
        config = Configuration("badusername", self.config_file)
        an = config.get_config_setting("account_number")
        print(an)
        assert an == "034477685180"

        """
        Test cases
        Config
        1. Pull missing parameters from macaw-auth section
        2. Pass all config via command line



        Credentials
        1. Create credential file if missing
        """