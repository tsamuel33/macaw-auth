import configparser
from pathlib import Path

class ConfigurationError(Exception):
    """Raises an exception when required configuration items are
    set incorrectly.

    Attributes:
        message -- message indicating the specifics of the error
    """

    def __init__(self,
            message='Incorrect configuration. Check your configuration file'):
        self.message = message
        super().__init__(self.message)

class Configuration:
    """
    A base class used to define various configurations used by the utility
    including role config and user credentials

    ...

    Attributes
    ----------
    # config_type : str
    #     username for validation
    # config_section : bool
    #     determines if the username is expected to be an email address
    # config_path : list
    #     list of valid symbols that can be included in username
    # config : bool
    #     boolean stating if provided username is valid
    # config_parameters :
    #     temp
    """

    default_configuration_file = Path.home() / ".aws" / "config"
    default_credentials_file = Path.home() / ".aws" / "credentials"

    def __init__(self, config_type, section_name, config_file=None):
        self.config_type = config_type
        self.config_path = self.select_config_file_path(
            config_type, config_file)
        self.config_section = self.select_config_section(section_name)
        self.config = self.initialize_config()

    # Set the configuration/credential file to use
    def select_config_file_path(self, file_type, file_path):
        if file_path is not None:
            config_path = file_path
        else:
            if file_type == 'user':
                config_path = self.default_configuration_file
            elif file_type == 'credential':
                config_path = self.default_credentials_file
            else:
                # The config type should be transparent to end users but add an
                # error just in case
                message = "Invalid config type passed: {}. ".format(file_type) + \
                    "Valid config types are 'user' and 'credential'"
                raise ConfigurationError(message)
        return config_path

    # Select which section of the configuration file will be used
    def select_config_section(self, section):
        if self.config_type == 'credential':
            if section is None:
                config_section = 'default'
            else:
                config_section = section
        elif self.config_type == 'user':
            if section is None:
                config_section = 'macaw-auth'
            else:
                config_section = 'profile ' + section
        else:
            # The config type should be transparent to end users but add an
            # error just in case
            message = "Invalid config type passed: {}. ".format(self.config_type) + \
                "Valid config types are 'user, and 'credential'"
            raise ConfigurationError(message)
        return config_section

    def initialize_config(self):
        # Check if config file already exists
        file_exists = Path.is_file(self.config_path)
        #TODO - build logic to avoid erroring out if user passes everything via command line
        #TODO - create credentials file if it doesn't exist. May do the same for config but probably not
        if not file_exists:
            message = "Configuration file: {} does not exist. ".format(
                self.config_path) + "Please create the file and set the " + \
                "configuration options"
            raise ConfigurationError(message)
        config = configparser.ConfigParser()
        config.read(self.config_path)
        if self.config_section not in config.sections():
            config.add_section(self.config_section)
        return config

    def get_config_setting(self, attribute):
        setting = self.config[self.config_section].get(attribute)
        # If value isn't found in profile, check macaw-auth section
        if setting is None and self.config_type == 'user' and self.config_section != 'macaw-auth':
            setting = self.config['macaw-auth'].get(attribute)
        return setting

    def set_config_value(self, attribute_name, value, required=False, default=''):
        if value is not None:
            self.config[self.config_section][attribute_name] = str(value)
        else:
            setting = self.get_config_setting(attribute_name)
            if setting is None:
                if required:
                    message = "Required configuration value is missing: " + attribute_name
                    raise ConfigurationError(message)
                else:
                    self.config[self.config_section][attribute_name] = default
            else:
                self.config[self.config_section][attribute_name] = setting
    
    def parse_config_parameters(self, parameters : dict):
        for key, value in parameters.items():
            self.set_config_value(key, value[0], value[1], value[2])