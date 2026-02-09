import configparser
from pathlib import Path

class ConfigurationError(Exception):
    """
    Raise an exception when required configuration items are set
    incorrectly.

    Attributes:
        message (str) : message indicating the specifics of the error
    """

    def __init__(self,
            message='Incorrect configuration. Check your config file'):
        self.message = message
        super().__init__(self.message)

class Configuration:
    """
    Define a base class used for various configurations used by the
    utility including role configuration and user credentials.

    Attributes:
        config_type (str): Config file type
        config_section (str): The section of the configuration file
            that will be used with macaw-auth commands
        default_config_section (str): The default configuration section
            that will be used if a section is not specified
        config_path (str): Location of the configuration file
        config (Configuration): The Configuration class object
        default_configuration_file (pathlib.Path): The default location
            of the configuration file
        default_credentials_file (pathlib.Path): The default location
            of the credentials file
    """

    default_configuration_file = Path.home() / ".aws" / "config"
    default_credentials_file = Path.home() / ".aws" / "credentials"

    def __init__(
            self, section_name, config_file=None,
            config_type : str = "configuration", **config_parameters):
        """
        Construct the attributes of the Configuration object.
        
        Arguments:
            section_name (str): The section of the configuration file
                that will be used with macaw-auth commands
            config_file (str): Location of the configuration file 
            config_type (str): Config file type
            config_parameters (kwargs): Extra parameters used for the
                Configuration class methods
        """

        self.config_type = config_type
        if self.config_type == "configuration":
            self.default_config_section = "macaw-auth"
        elif self.config_type == "credential":
            self.default_config_section = "default"
        self.config_path = self._select_config_file_path(config_file)
        self.config_section = self._select_config_section(section_name)
        self.config = self._initialize_config()
        if len(config_parameters) > 0:
            self._parse_config_parameters(config_parameters)

    def _select_config_file_path(self, file_path):
        """
        Select the configuration file to use. Uses the default
        configuration file if a config file path is not specified.

        Arguments:
            file_path (str): Path to the selected config file

        Returns:
            config_path (str): The path to the selected config file
        """

        if file_path is not None:
            config_path = file_path
        else:
            if self.config_type == 'configuration':
                config_path = self.default_configuration_file
            elif self.config_type == 'credential':
                config_path = self.default_credentials_file
        return config_path

    def _select_config_section(self, section=None):
        """
        Select the section of the configuration file to use. Uses the
        default section if a config section is not specified.

        Arguments:
            section (str): The name of the config section to use

        Returns:
            config_section (str): The config section that will be used
        """

        config_section = None
        if self.config_type == 'credential':
            if section is not None:
                config_section = section
        elif self.config_type == 'configuration':
            if section is not None:
                config_section = f"profile {section}"
        if config_section == None:
            config_section = self.default_config_section
        return config_section

    def _initialize_config(self):
        """
        Create the Configuration class object by loading the specified
        or default configuration file with provided parameters.
        
        Arguments:
            config_path (str): Location of the configuration file 

        Returns:
            config (Configuration): The Configuration class object
        """

        file_exists = Path.is_file(self.config_path)
        #TODO - build logic to avoid erroring out if user passes everything via command line
        #TODO - create credentials file if it doesn't exist. May do the same for config but probably not
        if not file_exists:
            message = f"Configuration file: {self.config_path} does " \
                      "not exist. Please create the file and set the" \
                      " configuration options"
            raise ConfigurationError(message)
        config = configparser.ConfigParser(
               default_section=self.default_config_section)
        config.read(self.config_path)
        if (self.config_section not in config.sections() and
                self.config_section != self.default_config_section):
            config.add_section(self.config_section)
        return config

    @staticmethod
    def arg_to_string(arg): #TODO - remove if possible, otherwise write a docstring
        if arg is not None:
            value = str(arg)
        else:
            value = arg
        return value

    def get_config_setting(self, attribute):
        """
        Get the selected attribute from the configuration file.

        Arguments:
            attribute (str): The name of the key for the desired value

        Returns:
            setting (str): The value of the specified attribute
        """

        setting = self.config[self.config_section].get(attribute)
        return setting

    def set_config_value(
            self, attribute_name, value,
            required=False, default=''):
        """
        Set the value of the selected attribute within the
        Configuration object.
        
        Arguments:
            attribute_name (str): The name of the attribute for which
                the value will be set
            value (str): The value to be set within the configuration
            required (bool): Denotes if the attribute is required or
                optional
            default (str): The default value of the attribute if no
                value is provided
        """

        if value is not None:
            self.config[self.config_section][attribute_name] = str(value)
        else:
            setting = self.get_config_setting(attribute_name)
            if setting is None:
                if required:
                    message = "Required configuration value is " \
                              f"missing: {attribute_name}"
                    raise ConfigurationError(message)
                else:
                    self.config[self.config_section][attribute_name] = default
            else:
                self.config[self.config_section][attribute_name] = setting
    
    def _parse_config_parameters(self, parameters : dict):
        """
        Set configuration values for any keyword arguments passed to
        the Configuration class.

        Arguments:
            parameters (kwargs): A set of keyword arguments to pass
                into the configuration
        """

        for key, value in parameters.items():
            self.set_config_value(
                key, self.arg_to_string(value[0]), value[1], value[2])

    def write_config(self):
        """
        Write the Configuration object to the specified configuration
        file.
        """

        with open(self.config_path, 'w+') as configfile:
            self.config.write(configfile)

        if self.config_type == "credential":
            print('\n\n')
            print('-'*64)
            print('Your new CLI credentials have been stored in the '
                  f'AWS configuration file {self.config_path} under '
                  f'the {self.config_section} profile.')
            print('Note that they will expire at '
                  '{}.'.format(self.config[self.config_section]['expiration']))
            print('After this time, you may safely rerun this script'
                  ' to refresh your credentials.')
            if self.config_section != 'default':
                print('To use this credential, call the AWS CLI with '
                      'the --profile option (e.g. aws --profile '
                      f'{self.config_section} ec2 describe-instances).')
            print('-'*64)
            print('\n\n')