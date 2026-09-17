import base64
import sys
import xml.etree.ElementTree as ET

import boto3

from macaw_auth.classes.configuration import Configuration
from macaw_auth.functions.common import arn_validation


class AWSSTSService:
    """
    Makes calls to the STS API to support various features of the tool

    Arguments:
        region (str): The AWS region to use
        access_key (str): The user's IAM access key (optional)
        secret_key (str): The user's IAM secret key (optional)
        session_token (str): The IAM session token for the user's
            credentials (optional)
        verify_ssl (bool): Whether the SSL certificate of the STS
            endpoint should be verified
    """

    def __init__(
        self,
        region="us-east-1",
        access_key=None,
        secret_key=None,
        session_token=None,
        verify_ssl=True,
    ):
        """
        Construct the attributes of the AWSSTSService object

        Attributes:
            region (str): AWS region in which STS calls will be made
            sts (boto3.client): STS Boto3 client
        """
        self.region = region
        self.sts = boto3.client(
            "sts",
            region_name=self.region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
            verify=verify_ssl,
        )

    def login(
        self,
        account_number,
        idp_name,
        role_name,
        saml_assertion,
        target_profile,
        credential_file,
        partition="aws",
        path="/",
        session_duration=3600,
        output_format="json",
    ):
        """
        Logs in to AWS and obtains session keys

        Arguments:
            account_number (str): AWS account number which user will log in to
            idp_name (str): Name of the IAM identity provider
            role_name (str): Name of the role to assume
            saml_assertion (xml): XML-formatted SAML assertion
            target_profile (str): Name of the profile in the credentials file
                in which the session keys will be stored
            credential_file (str): Location of the credentials file
            partition (str): The AWS partition used for login
            path (str): The optional path in the IAM role that will be assumed
            session_duration (int): Duration of the login session in seconds
            output_format (str): The format of command outputs (i.e., json)
        """
        empty = ["", None]
        if account_number in empty or idp_name in empty or role_name in empty:
            self.get_authorized_roles(saml_assertion)
        else:
            self.role_arn = self.generate_arn(
                partition, account_number, "role", role_name, path
            )
            self.principal_arn = self.generate_arn(
                partition, account_number, "saml", idp_name, path
            )
        self.__assume_role_response = self.assume_role_with_saml(
            saml_assertion, session_duration
        )
        self.__credentials = self.__assume_role_response["Credentials"]
        cred_parameters = {
            "region": (self.region, False, "us-east-1"),
            "output": (output_format, False, "json"),
            "aws_access_key_id": (self.__credentials["AccessKeyId"], True, ""),
            "aws_secret_access_key": (
                self.__credentials["SecretAccessKey"],
                True,
                "",
            ),
            "aws_session_token": (
                self.__credentials["SessionToken"],
                True,
                "",
            ),
            "expiration": (self.__credentials["Expiration"], True, ""),
        }
        self.__aws_creds = Configuration(
            target_profile, credential_file, "credential", **cred_parameters
        )
        self.__aws_creds.write_config()

    def assume(
        self,
        account_number,
        role_name,
        session_name,
        partition,
        path,
        duration,
    ):
        """
        Assumes an IAM role

        Arguments:
            account_number (str): AWS account number which user will log in to
            role_name (str): Name of the role to assume
            session_name (str): Name of the assumed role session
            partition (str): The AWS partition used for login
            path (str): The optional path in the IAM role that will be assumed
            duration (int): Duration of the login session in seconds
        """
        self.role_arn = self.generate_arn(
            partition, account_number, "role", role_name, path
        )
        self.assume_role(self.role_arn, session_name, duration)

    def get_role_session_name(self):
        """
        Gets the session name for role assumption. This value defaults to the
        user's ID

        Returns:
            session_name (str): Name of the assumed role session
        """
        response = self.sts.get_caller_identity()
        session_name = response["UserId"].split(":")[-1]
        return session_name

    def __default_arn_elements(self, value, element_type):
        return (
            "aws"
            if value is None and element_type == "partition"
            else "/"
            if value is None and element_type == "path"
            else value
        )

    def generate_arn(self, partition, account, iam_type, name, path):
        """
        Generates the ARN of the IAM role or SAML provider based on inputs

        Arguments:
            partition (str): The AWS partition used for login
            account (str): AWS account number which user will log in to
            iam_type (str): Determines whether the output will be an IAM role
                or SAML identity provider
            name (str): Name of the role or identity provider
            path (str): The optional path in the IAM role that will be assumed

        Returns:
            arn (str): The ARN of the IAM role or SAML identity provider
        """
        if iam_type == "saml":
            prefix = "saml-provider"
            cleaned_path = ""
        elif iam_type == "role":
            prefix = "role"
            cleaned_path = self.__default_arn_elements(path, "path")
            if path.startswith("/"):
                cleaned_path = cleaned_path[1 : len(cleaned_path)]
            if path.endswith("/"):
                cleaned_path = cleaned_path[:-1]
        suffix = name if len(cleaned_path) == 0 else f"{cleaned_path}/{name}"
        arn = "arn:{}:iam::{}:{}/{}".format(
            self.__default_arn_elements(partition, "partition"),
            account,
            prefix,
            suffix,
        )
        arn_validation(arn, iam_type)
        return arn

    # TODO - add error handling if user passes a bad role or principal arn
    # botocore.errorfactory.InvalidIdentityTokenException: An error occurred
    # (InvalidIdentityToken) when calling the AssumeRoleWithSAML operation:
    # SAML Assertion doesn't contain the requested Role and Metadata in the
    # attributes
    def assume_role_with_saml(self, assertion, duration):
        """
        Assumes IAM role via SAML

        Arguments:
            assertion (xml): XML-formatted SAML assertion
            duration (int): Duration of the login session in seconds

        Returns:
            response (str): The session credentials for the assumed role
        """
        response = self.sts.assume_role_with_saml(
            RoleArn=self.role_arn,
            PrincipalArn=self.principal_arn,
            SAMLAssertion=assertion,
            DurationSeconds=duration,
        )
        return response

    def get_authorized_roles(self, assertion):
        """
        Obtains a list of roles that the user is authorized to access via SAML

        Arguments:
            assertion (xml): XML-formatted SAML assertion
        """
        # Parse the returned assertion and extract the authorized roles
        awsroles = []
        root = ET.fromstring(base64.b64decode(assertion))
        for saml2attribute in root.iter(
            "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"
        ):
            if (
                saml2attribute.get("Name")
                == "https://aws.amazon.com/SAML/Attributes/Role"
            ):
                awsroles.extend(
                    saml2attributevalue.text
                    for saml2attributevalue in saml2attribute.iter(
                        "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue"
                    )
                )

        # Note the format of the attribute value should be
        # role_arn,principal_arn but lots of blogs list it as
        # principal_arn,role_arn so let's reverse them if needed
        for awsrole in awsroles:
            chunks = awsrole.split(",")
            if "saml-provider" in chunks[0]:
                newawsrole = chunks[1] + "," + chunks[0]
                index = awsroles.index(awsrole)
                awsroles.insert(index, newawsrole)
                awsroles.remove(awsrole)

        # If I have more than one role, ask the user which one they want,
        # otherwise just proceed
        print("")
        if len(awsroles) > 1:
            i = 0
            print("Please choose the role you would like to assume:")
            for i, awsrole in enumerate(awsroles):
                print("[", i, "]: ", awsrole.split(",")[0])
            print("Selection: ", end=" ")
            selectedroleindex = input()

            # Basic sanity check of input
            if int(selectedroleindex) > (len(awsroles) - 1):
                print("You selected an invalid role index, please try again")
                sys.exit(0)

            self.role_arn = awsroles[int(selectedroleindex)].split(",")[0]
            self.principal_arn = awsroles[int(selectedroleindex)].split(",")[1]
        else:
            self.role_arn = awsroles[0].split(",")[0]
            self.principal_arn = awsroles[0].split(",")[1]

    # TODO - Allow role assumption after login
    # TODO - Add ability to assume role using external ID and MFA
    def assume_role(self, role_arn, session_name, duration):
        """
        Assume an IAM role via AWS STS

        Arguments:
            role_arn (str): ARN of the role to assume
            session_name (str): Name of the assumed role session
            duration (int): Duration of the login session in seconds

        Returns:
            response (str): The session credentials for the assumed role
        """
        response = self.sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name,
            DurationSeconds=duration,
            # ExternalId='string',
            # SerialNumber='string',
            # TokenCode='string'
        )
        return response
