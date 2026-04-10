from getpass import getpass

from macaw_auth.classes.username_validation import UsernameValidation
from macaw_auth.classes.user_credentials import UserCredentials
from macaw_auth.classes.configuration import Configuration
from macaw_auth.classes.idp_connection import SAMLAssertion
from macaw_auth.classes.sts_saml import AWSSTSService

def get_username(name: str) -> str:
    print('Please enter your AWS login credentials.')
    if name != '':
        print(f'User ID: {name}')
        user = name
    else:
        user = input('User ID: ')
    return user

def main(args) -> None:
    client_parameters = {
        "session_duration": (args['duration_seconds'], False, '3600'),
        "identity_url": (args['identity_url'], True, ''),
        "enable_keyring": (args['enable_keyring'], False, 'False'),
        "account_number": (args['account_number'], False, ''),
        "idp_name": (args['idp_name'], False, ''),
        "role_name": (args['role_name'], False, ''),
        "region": (args['region'], False, 'us-east-1'),
        "output": (args['output'], False, 'json'),
        "connection_type": (args['auth_type'], False, 'web_form'),
        "path": (args['path'], False, '/'),
        "partition": (args['partition'], False, 'aws'),
    }

    print('Welcome! Checking your configuration files...')
    #TODO - change SOURCE_PROFILE to PROFILE_NAME
    config = Configuration(args['SOURCE_PROFILE'], args['config_file'], **client_parameters)
    config_user = config.get_config_setting("username")
    user = get_username(config_user)
    validation = UsernameValidation(user)
    user_creds = UserCredentials(validation.username, config.get_config_setting('identity_url'),
                                args['auth_type'], args['no_ssl'],
                                args['reset_password'], config.get_config_setting('enable_keyring'))
    sts_service = AWSSTSService(config.get_config_setting('region'),verify_ssl=args['no_ssl'])
    sts_service.login(config.get_config_setting('account_number'), config.get_config_setting('idp_name'), config.get_config_setting('role_name'),
                      user_creds.assertion, args['target_profile'], args['credential_file'],
                      config.get_config_setting('partition'), config.get_config_setting('path'), int(config.get_config_setting('session_duration')),
                      config.get_config_setting('output'))