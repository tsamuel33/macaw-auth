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

A sample config file can be found [here](https://github.com/tsamuel33/macaw-auth/blob/main/examples/config). Your config file should be stored in ~/.aws/config, but if you store it elsewhere, you can pass it to
macaw-auth using the **--credentials-file** flag. Be sure to update the following values in your config:

* identity_url

**NOTE:** You should also update the profile name(s) to be meaningful to you.

## Functions

The utility has been configured with several different functions as described below:

### Login

This function allows users to log in to their AWS environment. To use a profile that has been configured in your config file,
you can run the following command:

```text
macaw-auth login example-profile
```

The tool can also be called without the profile name and you will be presented with a list of roles to which you have access.

#### Login Help Output

```text
macaw-auth login -h
```

```text
usage: macaw-auth login [-h] [-a ACCOUNT_NUMBER] [--auth-type [{ntlm,web_form}]] [--config-file CONFIG_FILE] [--credential-file CREDENTIAL_FILE] [--disable-keyring] [--duration-seconds DURATION_SECONDS] [--identity-url IDENTITY_URL]
                        [--idp-name IDP_NAME] [-k] [--output {json,yaml,yaml-stream,text,table}] [--partition [{aws,aws-cn,aws-us-gov}]] [--path PATH] [--region REGION] [-r] [-n ROLE_NAME] [-t TARGET_PROFILE] [-u]
                        [SOURCE_PROFILE]

positional arguments:
  SOURCE_PROFILE        Name of the profile in your config file containing the desired settings

options:
  -h, --help            show this help message and exit
  -a ACCOUNT_NUMBER, --account-number ACCOUNT_NUMBER
                        AWS account number to log in to.
  --auth-type [{ntlm,web_form}]
                        Authorization type used for SAML request
  --config-file CONFIG_FILE
                        Path to config file if ~/.aws/config will not be used
  --credential-file CREDENTIAL_FILE
                        Path to credential file if ~/.aws/credentials will not be used
  --disable-keyring     Disable storing password in keyring
  --duration-seconds DURATION_SECONDS
                        Length of time in seconds in which credentials are valid
  --identity-url IDENTITY_URL
                        URL used to initiate SAML request
  --idp-name IDP_NAME   Name of the AWS IAM identity provider resource used for the SAML request
  -k, --no-ssl-verify   Make insecure SAML request
  --output {json,yaml,yaml-stream,text,table}
                        The desired AWS CLI output format
  --partition [{aws,aws-cn,aws-us-gov}]
                        The AWS partition associated with the desired region
  --path PATH           The optional path used in the IAM role ARN
  --region REGION       Default AWS region for CLI commands
  -r, --reset-password  Reset keyring password
  -n ROLE_NAME, --role-name ROLE_NAME
                        The name of your IAM role
  -t TARGET_PROFILE, --target-profile TARGET_PROFILE
                        Name of the section where credentials will be stored in the credentials file
  -u, --username-not-email
                        Indicates that the supplied username will not need to be in an email format
```

### Assume-Role

This function allows users to assume a role using existing credentials in their credentials file. The assumed role can be
configured in your config file, or you can pass the full role ARN. This function can be called by running the following command:

```text
macaw-auth assume-role example-profile
```

or

```text
macaw-auth assume-role arn:aws:iam::123456789012:role/samplepath/Admin
```

#### Assume-Role Help Output

```text
macaw-auth assume-role -h
```

```text
usage: macaw-auth assume-role [-h] [--config-file CONFIG_FILE] [--credential-file CREDENTIAL_FILE] [--region REGION] [-s SOURCE] [-t TARGET_PROFILE] ROLE

positional arguments:
  ROLE                  Name of the profile containing the assumed role's configuration or the ARN of the role to assume

options:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        Path to config file if ~/.aws/config will not be used
  --credential-file CREDENTIAL_FILE
                        Path to credential file if ~/.aws/credentials will not be used
  --region REGION       Default AWS region for CLI commands
  -s SOURCE, --source SOURCE
                        Name of profile containing the credentials that can assume the target role
  -t TARGET_PROFILE, --target-profile TARGET_PROFILE
                        Name of the section where credentials will be stored in the credentials file
```

### Web

This functions allows you to log in to the AWS console using the credentials of the specified profile. This
function can be called by running the following command:

```text
macaw-auth web example-profile
```

**NOTE:** To avoid conflicting credentials from an existing console session, this command performs a logout, then logs in 3 seconds later.

#### Web Help Output

```text
macaw-auth web -h
```

```text
usage: macaw-auth web [-h] [--credential-file CREDENTIAL_FILE] [--duration-seconds DURATION_SECONDS] [-k] [--region REGION] [PROFILE]

positional arguments:
  PROFILE               Name of the profile containing the credentials to use for AWS console log in

options:
  -h, --help            show this help message and exit
  --credential-file CREDENTIAL_FILE
                        Path to credential file if ~/.aws/credentials will not be used
  --duration-seconds DURATION_SECONDS
                        Length of time in seconds in which credentials are valid
  -k, --no-ssl-verify   Make insecure SAML request
  --region REGION       AWS region to access via the console
```

## Troubleshooting

### Clear Saved Password

If you receive an error indicating that there's no valid SAML assertation, please double check your config settings. If you have keyring enabled, you may have stored
an incorrect password. To reset your keyring password, run one of the following commands:

```text
macaw-auth login -r
```

or

```text
macaw-auth login --reset-password
```

### Errors Logging In With Keyring Enabled

This utility gives the option to use [Keyring](https://pypi.org/project/keyring/) to locally store your password. If you attempt to use Keyring and do not have a proper backend set up as stated in the Keyring documentation, macaw-auth may not work. To disable Keyring, use one of the following options:

#### 1. **Disable Keyring in Config File**

In your config file, you can set ```enable_keyring = False``` in the **[macaw-auth]** section

#### 2. **Disable Keyring via CLI**

When running macaw-auth commands, you can add the **--disable-keyring** flag (e.g., ```macaw-auth login --disable-keyring```).

### SSLError Exception

If you encounter the **requests.exceptions.SSLError** error while attempting an initial log in or attempting to reach the AWS console,
you can make an insecure network call by running:

```text
macaw-auth login -k
```

or

```text
macaw-auth web --no-ssl-verify
```
