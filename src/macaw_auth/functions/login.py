import platform
import sys
from ..classes.username_validation import UsernameValidation
from ..classes.user_credentials import UserCredentials
from ..classes.configuration import Configuration
from ..classes.idp_connection import SAMLAssertion
from ..classes.sts_saml import AWSSTSService
from ..classes.aws_credentials import AWSCredentials
# from .cli import main as cli_main
from getpass import getpass

def arg_to_string(arg) -> str:
    if arg is not None:
        value = str(arg)
    else:
        value = arg
    return value

#TODO - loop through usage of arg_to_string

def get_username(name: str) -> str:
    print('Please enter your AWS login credentials.')
    if name != '':
        print('User ID: {}'.format(name))
        user = name
    else:
        user = input('User ID: ')
    return user

def main(args) -> None:
    # args = cli_main()
    #FOR DEBUGGING
    # print(args)

    print('Welcome! Checking your configuration files...')
    client_config = Configuration('user', arg_to_string(args['SOURCE_PROFILE']),
                           arg_to_string(args['config_file']))
                        #    session_duration=(arg_to_string(args['duration_seconds']),False, '3600'),
                        #    identity_url=(arg_to_string(args['identity_url']),True, ''),
                        #    enable_keyring=(arg_to_string(args['enable_keyring']),False, 'False'),
                        #    username=(None, False, ''),
                        #    account_number=(arg_to_string(args['account_number']),False, ''),
                        #    idp_name=(arg_to_string(args['idp_name']),False, ''),
                        #    role_name=(arg_to_string(args['role_name']),False, ''),
                        #    region=(arg_to_string(args['region']),False, 'us-east-1'),
                        #    output=(arg_to_string(args['output']),False, 'json'),
                        #    connection_type=(arg_to_string((args['auth_type'])),False, 'web_form'),
                        #    path=(arg_to_string(args['path']),False, '/'),
                        #    partition=(arg_to_string(args['partition']),False, 'aws'))
    client_parameters = {
        "session_duration": (arg_to_string(args['duration_seconds']),False, '3600'),
        "identity_url": (arg_to_string(args['identity_url']),True, ''),
        "enable_keyring": (arg_to_string(args['enable_keyring']),False, 'False'),
        "username": (None, False, ''),
        "account_number": (arg_to_string(args['account_number']),False, ''),
        "idp_name": (arg_to_string(args['idp_name']),False, ''),
        "role_name": (arg_to_string(args['role_name']),False, ''),
        "region": (arg_to_string(args['region']),False, 'us-east-1'),
        "output": (arg_to_string(args['output']),False, 'json'),
        "connection_type": (arg_to_string((args['auth_type'])),False, 'web_form'),
        "path": (arg_to_string(args['path']),False, '/'),
        "partition": (arg_to_string(args['partition']),False, 'aws')
    }
    client_config.parse_config_parameters(client_parameters)
    client = client_config.config[client_config.config_section]
    user = get_username(client['username'])
    validation = UsernameValidation(user, args['username_not_email'])
    user_creds = UserCredentials(validation.username, client['identity_url'], args['auth_type'], args['no_ssl'], args['reset_password'], client['enable_keyring'])
    roles = AWSSTSService(user_creds.assertion, client['account_number'], client['idp_name'], client['role_name'], client['path'], client['partition'], int(client['session_duration']), client['region'])
    #TODO - Call AWSCredentials class within AWSSTSService class
    aws_creds = AWSCredentials('credential', arg_to_string(args['target_profile']),
                                arg_to_string(args['credential_file']),
                                region=(client['region'],False, 'us-east-1'),
                                output=(client['output'],False, 'json'),
                                aws_access_key_id=(roles._aws_access_key_id, True, ''),
                                aws_secret_access_key=(roles._aws_secret_access_key, True, ''),
                                aws_session_token=(roles._aws_session_token, True, ''),
                                expiration=(roles._expiration,True, ''))

if __name__ == '__main__':
    sys.exit(main())



    # print('The client is running on the {} platform'.format(platform.system()))
    # sys.exit(main())