import base64
import boto3
import sys
import xml.etree.ElementTree as ET

class AWSSTSService:

    def __init__(
            self, saml_assertion, principal_arn, role_arn=None,
            session_duration=3600, region='us-east-1'):
        self.sts = boto3.client('sts', region_name=region)
        self.principal_arn = principal_arn
        self.saml_assertion = saml_assertion
        #TODO - Add validation for principal_arn as well
        if role_arn == '' or role_arn is None or principal_arn == '' or principal_arn is None:
            self.get_authorized_roles()
        else:
            self.role_arn = role_arn
            self.principal_arn = principal_arn
        self.duration = session_duration
        self.__credentials = self.assume_role_with_saml()['Credentials']
        self.split_creds()


    def assume_role_with_saml(self):
        response = self.sts.assume_role_with_saml(
            RoleArn=self.role_arn,
            PrincipalArn=self.principal_arn,
            SAMLAssertion=self.saml_assertion,
            DurationSeconds=self.duration
        )
        return response
    
    def get_authorized_roles(self):
        # Parse the returned assertion and extract the authorized roles
        awsroles = []
        root = ET.fromstring(base64.b64decode(self.saml_assertion))
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
        print(self.role_arn)
        print(self.principal_arn)

    def split_creds(self):
        self._aws_access_key_id = self.__credentials['AccessKeyId']
        self._aws_secret_access_key = self.__credentials['SecretAccessKey']
        self._aws_session_token = self.__credentials['SessionToken']
        self._expiration = self.__credentials['Expiration']

    # TODO - Allow role assumption after login
    def assume_role(self):
        response = self.sts.assume_role(
            RoleArn='string',
            RoleSessionName='string',
            PolicyArns=[
                {
                    'arn': 'string'
                },
            ],
            Policy='string',
            DurationSeconds=123,
            Tags=[
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ],
            TransitiveTagKeys=[
                'string',
            ],
            ExternalId='string',
            SerialNumber='string',
            TokenCode='string',
            SourceIdentity='string'
        )