import base64
import boto3
import sys
import xml.etree.ElementTree as ET

from macaw_auth.classes.aws_credentials import AWSCredentials
from macaw_auth.functions.common import arn_validation

class AWSSTSService:

    def __init__(
            self, saml_assertion=None, account_number=None, idp_name=None, role_name=None, path="/",
            partition="aws", session_duration=3600, region='us-east-1', output_format='json', args=None,
            action="login", access_key=None, secret_key=None, session_token=None):
        self.sts = boto3.client('sts', region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, aws_session_token=session_token)
        if action == "login":
            self.login(account_number, idp_name, role_name, saml_assertion, partition,
                       path, session_duration, region, output_format, args['target_profile'],
                       args['credential_file'])
        elif action == "assume_role":
            pass

    def login(self, account_number, idp_name, role_name, saml_assertion, partition,
              path, session_duration, region, output_format, target_profile, credential_file):
        #TODO - Add validation for principal_arn as well
        empty = ['', None]
        if account_number in empty or idp_name in empty or role_name in empty:
            self.get_authorized_roles(saml_assertion)
        else:
            self.role_arn = self.generate_arn(partition, account_number, "role", role_name, path)
            self.principal_arn = self.generate_arn(partition, account_number, "saml", idp_name)
        self.duration = session_duration
        self.__assume_role_response = self.assume_role_with_saml(saml_assertion)
        self.__credentials = self.__assume_role_response['Credentials']
        self.split_creds()
        self.cred_parameters = {
            "region": (region, False, 'us-east-1'),
            "output": (output_format, False, 'json'),
            "aws_access_key_id": (self.__aws_access_key_id, True, ''),
            "aws_secret_access_key": (self.__aws_secret_access_key, True, ''),
            "aws_session_token": (self.__aws_session_token, True, ''),
            "expiration": (self.__expiration, True, '')
        }
        self.__aws_creds = AWSCredentials('credential', target_profile,
                            credential_file, **self.cred_parameters)

    def generate_arn(self, partition, account, iam_type, name, path="/"):
        if iam_type == "saml":
            prefix = "saml-provider"
            cleaned_path = ""
        elif iam_type == "role":
            prefix = "role"
            cleaned_path = path
            if path.startswith("/"):
                cleaned_path = cleaned_path[1:len(cleaned_path)]
            if path.endswith("/"):
                cleaned_path = cleaned_path[:-1]
        if len(cleaned_path) == 0:
            suffix = name
        else:
            suffix = "/".join((cleaned_path, name))
        arn = "arn:{}:iam::{}:{}/{}".format(partition, account, prefix, suffix)
        return arn

    #TODO - add error handling if user passes a bad role or principal arn
    #botocore.errorfactory.InvalidIdentityTokenException: An error occurred (InvalidIdentityToken) when calling the AssumeRoleWithSAML operation: SAML Assertion doesn't contain the requested Role and Metadata in the attributes
    def assume_role_with_saml(self, assertion):
        response = self.sts.assume_role_with_saml(
            RoleArn=self.role_arn,
            PrincipalArn=self.principal_arn,
            SAMLAssertion=assertion,
            DurationSeconds=self.duration
        )
        return response

    def get_authorized_roles(self, assertion):
        # Parse the returned assertion and extract the authorized roles
        awsroles = []
        root = ET.fromstring(base64.b64decode(assertion))
        for saml2attribute in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
            if (saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role'):
                for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                    awsroles.append(saml2attributevalue.text)

        # Note the format of the attribute value should be role_arn,principal_arn
        # but lots of blogs list it as principal_arn,role_arn so let's reverse
        # them if needed
        for awsrole in awsroles:
            chunks = awsrole.split(',')
            if'saml-provider' in chunks[0]:
                newawsrole = chunks[1] + ',' + chunks[0]
                index = awsroles.index(awsrole)
                awsroles.insert(index, newawsrole)
                awsroles.remove(awsrole)

        # If I have more than one role, ask the user which one they want,
        # otherwise just proceed
        print("")
        if len(awsroles) > 1:
            i = 0
            print("Please choose the role you would like to assume:")
            for awsrole in awsroles:
                print('[', i, ']: ', awsrole.split(',')[0])
                i += 1
            print("Selection: ", end=' ')
            selectedroleindex = input()

            # Basic sanity check of input
            if int(selectedroleindex) > (len(awsroles) - 1):
                print('You selected an invalid role index, please try again')
                sys.exit(0)

            self.role_arn = awsroles[int(selectedroleindex)].split(',')[0]
            self.principal_arn = awsroles[int(selectedroleindex)].split(',')[1]
        else:
            self.role_arn = awsroles[0].split(',')[0]
            self.principal_arn = awsroles[0].split(',')[1]

    def split_creds(self):
        self.__aws_access_key_id = self.__credentials['AccessKeyId']
        self.__aws_secret_access_key = self.__credentials['SecretAccessKey']
        self.__aws_session_token = self.__credentials['SessionToken']
        self.__expiration = self.__credentials['Expiration']

    # TODO - Allow role assumption after login
    # TODO - Add ability to assume role using external ID and MFA
    def assume_role(self):
        response = self.sts.assume_role(
            RoleArn='string',
            RoleSessionName='string',
            DurationSeconds=self.duration,
            # ExternalId='string',
            # SerialNumber='string',
            # TokenCode='string'
        )