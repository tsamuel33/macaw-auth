import argparse
import sys
from importlib.metadata import version
from .functions.login import main as login_func

"""
section_name(Source Profile) - position argument

ssl_verification - flag
reset_password - flag

enable_keyring - flag or option?. should this be enabled or disabled by default?
auth_type - option
session_duration -option
identity_url - option
region - option
output - option
principal_arn - option
role_arn - option
target_profile - option
home_directory - option
config_file - option

username_is_email - change to username_is_iam and set as flag?

"""

def setup_main_parser():
    parser = argparse.ArgumentParser(prog='macaw-auth', description='Utility to authenticate to AWS Services via CLI')
    parser.add_argument('-v', '--version', action='version', version=version("macaw-auth"))
    return parser

def setup_login_parser(subparser):
    parser = subparser.add_parser('login')
    parser.add_argument('SOURCE_PROFILE', help='Name of the profile in your config file containing the desired settings', nargs='?', default=None)
    parser.add_argument('-a', '--account-number', help='AWS account number to log in to.')
    parser.add_argument('--auth-type', help='Authorization type used for SAML request', choices=['ntlm', 'web_form'], nargs='?', default='web_form')
    parser.add_argument('--config-file', help='Path to config file if ~/.aws/config will not be used')
    parser.add_argument('--credential-file', help='Path to credential file if ~/.aws/credentials will not be used')
    parser.add_argument('--disable-keyring', action='store_const', help='Disable storing password in keyring', const=False, dest='enable_keyring')
    parser.add_argument('--duration-seconds', help="Length of time in seconds in which credentials are valid", type=int)
    parser.add_argument('--identity-url', help='URL used to initiate SAML request')
    parser.add_argument('--idp-name', help='Name of the AWS IAM identity provider resource used for the SAML request')
    parser.add_argument('-k', '--no-ssl-verify', action='store_false', help='Make insecure SAML request', dest='no_ssl')
    parser.add_argument('--output', help='The desired AWS CLI output format', choices=['json', 'yaml', 'yaml-stream', 'text', 'table'])
    parser.add_argument('--partition', help='The AWS partition associated with the desired region', choices=['aws', 'aws-cn', 'aws-us-gov'], nargs='?', default='aws')
    parser.add_argument('--path', help='The optional path used in the IAM role ARN')
    parser.add_argument('--region', help='Default AWS region for CLI commands')
    parser.add_argument('-r', '--reset-password', action='store_true', help='Reset keyring password')
    parser.add_argument('-n', '--role-name', help='The name of your IAM role')
    parser.add_argument('-t', '--target-profile', help='Name of the section where credentials will be stored in the credentials file', type=str)
    parser.add_argument('-u', '--username-not-email', action='store_false', help='Indicates that the supplied username will not need to be in an email format')
    parser.set_defaults(func=login_func)
    return parser

def setup_assumerole_parser(subparser):
    parser = subparser.add_parser('assume-role')
    return parser

def setup_web_parser(subparser):
    parser = subparser.add_parser('web')
    return parser

def setup_timeleft_parser(subparser):
    parser = subparser.add_parser('time-left')
    return parser

def setup_refresh_parser(subparser):
    parser = subparser.add_parser('refresh')
    return parser

def setup_ecrlogin_parser(subparser):
    parser = subparser.add_parser('ecr-login')
    return parser

def arg_setup():
    parser = setup_main_parser()
    commands = parser.add_subparsers(title='commands', description='Available Commands', help='Valid Commands')
    login = setup_login_parser(commands)
    assumerole = setup_assumerole_parser(commands)
    # web = setup_web_parser(commands)
    # timeleft = setup_timeleft_parser(commands)
    # refresh = setup_refresh_parser(commands)
    # ecrlogin = setup_ecrlogin_parser(commands)
    args = parser.parse_args()
    # If user does not pass a subcommand, display the help options
    if 'func' in vars(args):
        return args
    else:
        parser.print_help()
        sys.exit(1)


def main():
    args = arg_setup()
    args.func(vars(args))

if __name__ == "__main__":
    main()