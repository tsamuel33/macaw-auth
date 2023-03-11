# macaw-auth

## Description

This repository contains code used to run the macaw-auth utility. Named after the
Hyacinth and Scarlet Macaws of the Amazon Rainforest, this tool allows users to
authenticate to ADFS to obtain their AWS credentials for use with the AWS CLI.

## Prequisites

The user should have the following tools installed:

* AWS CLI
* Python 3.X

## Installation

Install the tool using the following command

```
pip install "macaw-auth @ git+https://github.com/tsamuel33/macaw-auth
```

### Usage

```
macaw-auth -h
```

#### Output
```
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