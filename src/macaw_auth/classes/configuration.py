import configparser
from pathlib import Path
from .errors import ConfigurationError

class Configuration:
    """
    A base class used to define various configurations used by the utility
    including client config, role config, and user credentials

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

    def __init__(
            self, config_type, section_name, config_file=None,
            **config_parameters : tuple):
        self.config_type = config_type
        self.config_path = self.select_config_file_path(
            config_type, config_file)
        self.config_section = self.select_config_section(section_name)
        self.config = self.initialize_config()
        self.config_parameters = config_parameters
        self.parse_config_parameters()

    # Set the configuration/credential file to use
    def select_config_file_path(self, file_type, file_path):
        if file_path is not None:
            config_path = file_path
        else:
            if file_type == 'client' or file_type == 'user':
                config_path = self.default_configuration_file
            elif file_type == 'credential':
                config_path = self.default_credentials_file
            else:
                # The config type should be transparent to end users but add an
                # error just in case
                message = "Invalid config type passed: {}. ".format(file_type) + \
                    "Valid config types are 'client', 'user, and 'credential'"
                raise Configuration(message)
        return config_path

    # Select which section of the configuration file will be used
    def select_config_section(self, section):
        if self.config_type == 'credential':
            if section is None:
                config_section = 'default'
            else:
                config_section = section
        elif section is None:
            config_section = 'macaw-auth'
        elif self.config_type == 'client':
            config_section = section
        elif self.config_type == 'user':
            config_section = 'profile ' + section
        else:
            # The config type should be transparent to end users but add an
            # error just in case
            message = "Invalid config type passed: {}. ".format(self.config_type) + \
                "Valid config types are 'client', 'user, and 'credential'"
            raise Configuration(message)
        return config_section

    def initialize_config(self):

        # if self.config_section is None:
        #     config = configparser.ConfigParser()
        # else:


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
        # if self.config_section is None:
        #     return None
        # else:
        setting = self.config[self.config_section].get(attribute)
        return setting

    def set_optional_setting(self, setting, default):
        # if self.config_section is None:
        #     self.config.add_section('None')
        #     self.config['None'][setting] = default
        #     print(self.config['None'][setting])
        # else:
        value = self.get_config_setting(setting)
        if value is None:
            self.config[self.config_section][setting] = default

    def get_required_setting(self, attribute):
        # if self.config_section is None:
        #     message = "Required configuration value: {} ".format(attribute) + \
        #         "was not provided via command line and no profile was selected."
        #     raise ConfigurationError(message)
        # else:
        value = self.get_config_setting(attribute)
        if value is None:
            message = "Required configuration value is missing: " + attribute
            raise ConfigurationError(message)

    def set_config_value(self, attribute_name, value, required=False, default=''):
        if value is not None:
            # if self.config_section is None:
            #     self.config[attribute_name] = str(value)
            # else:
            self.config[self.config_section][attribute_name] = str(value)
        elif required:
            self.get_required_setting(attribute_name)
        else:
            self.set_optional_setting(attribute_name, default)
    
    def parse_config_parameters(self):
        for key, value in self.config_parameters.items():
            self.set_config_value(key, value[0], value[1], value[2])