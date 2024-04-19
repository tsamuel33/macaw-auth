# macaw-auth

## Description

This repository contains code used to run the macaw-auth utility. Named after the
Hyacinth and Scarlet Macaws of the Amazon Rainforest, this tool allows users to
authenticate to ADFS to obtain their AWS credentials for use with the AWS CLI.

## Prequisites

The user should have the following tools installed:

* AWS CLI
* Python 3.7+

**NOTE:** [Rust](https://www.rust-lang.org/) may be required when installing on Debian Linux systems.

## Installation

Install the tool using the following command

```text
pip install macaw-auth
```

### Usage

A sample config file can be found [here](https://github.com/tsamuel33/macaw-auth/blob/main/examples/config). Your config file should be stored in ~/.aws/config, but if you store it elsewhere, you can pass it to
macaw-auth using the **--credentials-file** flag. Be sure to update the following values in your config:

* identity_url
* username
* role_arn
* principal_arn

You should also update the profile name(s) to be meaningful to you. To use the role specified in the example config, call the tool using the following command:

```text
macaw-auth example-profile
```

The tool can also be called without the profile name and you will be presented with a list of roles to which you have access.

#### Help Output

```text
macaw-auth -h
```

```text
usage: macaw-auth [-h] [--no-ssl-verify] [-r] [-a [{ntlm,web_form}]] [--duration-seconds DURATION_SECONDS]
                     [--identity-url IDENTITY_URL] [--disable-keyring] [--region REGION]
                     [--output {json,yaml,yaml-stream,text,table}] [--role-arn ROLE_ARN]
                     [--principal-arn PRINCIPAL_ARN] [--target-profile TARGET_PROFILE] [--config-file CONFIG_FILE]
                     [--credential-file CREDENTIAL_FILE] [--username-not-email]
                     [SOURCE_PROFILE]

Utility to obtain AWS CLI credentials

positional arguments:
  SOURCE_PROFILE        Name of the profile in your config file containing the desired configuration

options:
  -h, --help            show this help message and exit
  --no-ssl-verify       Make insecure SAML request
  -r, --reset-password  Reset keyring password
  -a [{ntlm,web_form}], --auth-type [{ntlm,web_form}]
                        Authorization type used for SAML request
  --duration-seconds DURATION_SECONDS
                        Length of time in seconds in which credentials are valid
  --identity-url IDENTITY_URL
                        URL used to initiate SAML request
  --disable-keyring     Disable storing password in keyring
  --region REGION       Default AWS region for CLI commands
  --output {json,yaml,yaml-stream,text,table}
                        The desired AWS CLI output format
  --role-arn ROLE_ARN   ARN of the role that you want to assume
  --principal-arn PRINCIPAL_ARN
                        ARN of the IAM SAML provider that describes the IdP
  --target-profile TARGET_PROFILE
                        Name of the section where credentials will be stored in the credentials file
  --config-file CONFIG_FILE
                        Path to config file if ~/.aws/config will not be used
  --credential-file CREDENTIAL_FILE
                        Path to credential file if ~/.aws/credentials will not be used
  --username-not-email  Indicates that the supplied username will not need to be in an email format
```

## Troubleshooting

### Clear Saved Password

If you receive an error indicating that there's no valid SAML assertation, please double check your config settings. If you have keyring enabled, you may have stored
an incorrect password. To reset your keyring password, run one of the following commands:

```text
macaw-auth -r
```

or

```text
macaw-auth --reset-password
```

### Errors Running the Utility With Keyring Enabled

This utility gives the option to use [Keyring](https://pypi.org/project/keyring/) to locally store your password. If you attempt to use Keyring and do not have a proper backend set up as stated in the Keyring documentation, macaw-auth may not work. To disable Keyring, use one of the following options:

#### 1. **Disable Keyring in Config File**

In your config file, you can set ```enable_keyring = False``` in the **[macaw-auth]** section

#### 2. **Disable Keyring via CLI**

When running macaw-auth commands, you can add the **--disable-keyring** flag (e.g., ```macaw-auth --disable-keyring```).
