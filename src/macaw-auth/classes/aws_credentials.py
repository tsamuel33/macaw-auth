from .configuration import Configuration

class AWSCredentials(Configuration):

    def __init__(self, config_type, target_profile, config_file=None, **config_parameters: tuple):
        super().__init__(config_type, target_profile, config_file, **config_parameters)
        self.region = self.config[self.config_section]['region']
        self.output = self.config[self.config_section]['output']
        self.set_credential_config()
        self.write_config()

    def set_credential_config(self):
        self.config.set(self.config_section, 'region', self.region)
        self.config.set(self.config_section, 'output', self.output)
        cred_map = self.config[self.config_section]
        self.config.set(self.config_section, 'aws_access_key_id', cred_map['aws_access_key_id'])
        self.config.set(self.config_section, 'aws_secret_access_key', cred_map['aws_secret_access_key'])
        self.config.set(self.config_section, 'aws_session_token', cred_map['aws_session_token'])

    def write_config(self):
        # Write the updated config file
        with open(self.config_path, 'w+') as configfile:
            self.config.write(configfile)

        # Give the user some basic info as to what has just happened
        print('\n\n----------------------------------------------------------------')
        print('Your new access key pair has been stored in the AWS configuration file {0} under the {1} profile.'.format(self.config_path, self.config_section))
        print('Note that it will expire at {0}.'.format(self.config[self.config_section]['expiration']))
        print('After this time, you may safely rerun this script to refresh your access key pair.')
        if self.config_section != 'default':
            print('To use this credential, call the AWS CLI with the --profile option (e.g. aws --profile {0} ec2 describe-instances).'.format(self.config_section))
        print('----------------------------------------------------------------\n\n')