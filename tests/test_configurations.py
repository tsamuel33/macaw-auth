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

    def test_use_non_existent_config_path(self):
        config_path = Path.cwd() / "tests" / "test_files" / "config2"
        with pytest.raises(ConfigurationError, match="does not exist"):
            Configuration("use-defaults", config_path)

    def test_use_non_existent_config_path(self):
        config_path = Path.cwd()/"tests"/"test_files"/"credentials2"
        Configuration("use-defaults", config_path, "credential")
        assert Path.is_file(config_path)