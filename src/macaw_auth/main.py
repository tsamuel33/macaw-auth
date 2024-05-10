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

def arg_setup():
    parser = argparse.ArgumentParser(prog='macaw-auth', description='Utility to authenticate to AWS Services via CLI')
    parser.add_argument('-v', '--version', action='version', version=version("macaw-auth"))
    commands = parser.add_subparsers(title='commands', description='Available Commands', help='Valid Commands')
    login = commands.add_parser('login')
    # assumerole = commands.add_parser('assume-role')
    # web = commands.add_parser('web')
    # timeleft = commands.add_parser('time-left')
    # refresh = commands.add_parser('refresh')
    # ecrlogin = commands.add_parser('ecr-login')
    login.add_argument('SOURCE_PROFILE', help='Name of the profile in your config file containing the desired settings', nargs='?', default=None)
    login.add_argument('-a', '--account-number', help='AWS account number to log in to.')
    login.add_argument('--auth-type', help='Authorization type used for SAML request', choices=['ntlm', 'web_form'], nargs='?', default='web_form')
    login.add_argument('--config-file', help='Path to config file if ~/.aws/config will not be used')
    login.add_argument('--credential-file', help='Path to credential file if ~/.aws/credentials will not be used')
    login.add_argument('--disable-keyring', action='store_const', help='Disable storing password in keyring', const=False, dest='enable_keyring')
    login.add_argument('--duration-seconds', help="Length of time in seconds in which credentials are valid", type=int)
    login.add_argument('--identity-url', help='URL used to initiate SAML request')
    login.add_argument('--idp-name', help='Name of the AWS IAM identity provider resource used for the SAML request')
    login.add_argument('-k', '--no-ssl-verify', action='store_false', help='Make insecure SAML request', dest='no_ssl')
    login.add_argument('--output', help='The desired AWS CLI output format', choices=['json', 'yaml', 'yaml-stream', 'text', 'table'])
    login.add_argument('--partition', help='The AWS partition associated with the desired region', choices=['aws', 'aws-cn', 'aws-us-gov'], nargs='?', default='aws')
    login.add_argument('--path', help='The optional path used in the IAM role ARN')
    login.add_argument('--region', help='Default AWS region for CLI commands')
    login.add_argument('-r', '--reset-password', action='store_true', help='Reset keyring password')
    login.add_argument('-n', '--role-name', help='The name of your IAM role')
    login.add_argument('-t', '--target-profile', help='Name of the section where credentials will be stored in the credentials file', type=str)
    login.add_argument('-u', '--username-not-email', action='store_false', help='Indicates that the supplied username will not need to be in an email format')
    login.set_defaults(func=login_func)
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