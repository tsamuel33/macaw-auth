from getpass import getpass

from macaw_auth.classes.username_validation import UsernameValidation
from macaw_auth.classes.user_credentials import UserCredentials
from macaw_auth.classes.configuration import Configuration
from macaw_auth.classes.idp_connection import SAMLAssertion
from macaw_auth.classes.sts_saml import AWSSTSService

def get_username(name: str) -> str:
    print('Please enter your AWS login credentials.')
    if name != '':
        print('User ID: {}'.format(name))
        user = name
    else:
        user = input('User ID: ')
    return user

def main(args) -> None:

    client_parameters = {
        "session_duration": (args['duration_seconds'], False, '3600'),
        "identity_url": (args['identity_url'], True, ''),
        "enable_keyring": (args['enable_keyring'], False, 'False'),
        "username": (None, False, ''),
        "account_number": (args['account_number'], False, ''),
        "idp_name": (args['idp_name'], False, ''),
        "role_name": (args['role_name'], False, ''),
        "region": (args['region'], False, 'us-east-1'),
        "output": (args['output'], False, 'json'),
        "connection_type": (args['auth_type'], False, 'web_form'),
        "path": (args['path'], False, '/'),
        "partition": (args['partition'], False, 'aws')
    }

    print('Welcome! Checking your configuration files...')
    client_config = Configuration('user', args['SOURCE_PROFILE'],
                           args['config_file'], **client_parameters)
    client = client_config.config[client_config.config_section]
    user = get_username(client['username'])
    validation = UsernameValidation(user, args['username_not_email'])
    user_creds = UserCredentials(validation.username, client['identity_url'],
                                args['auth_type'], args['no_ssl'],
                                args['reset_password'], client['enable_keyring'])
    sts_service = AWSSTSService(client['region'])
    sts_service.login(client['account_number'], client['idp_name'], client['role_name'],
                      user_creds.assertion, args['target_profile'], args['credential_file'],
                      client['partition'], client['path'], int(client['session_duration']),
                      client['output'])