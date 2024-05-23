from botocore.exceptions import ClientError

from macaw_auth.functions.common import arn_validation
from macaw_auth.classes.configuration import Configuration
from macaw_auth.classes.sts_saml import AWSSTSService


class RoleAssumptionError(Exception):
    """Raises an exception encountering an error while trying
    to assume a fole.

    Attributes:
        message -- message indicating the specifics of the error
    """

    def __init__(self,
            message='Incorrect configuration. Check your configuration file'):
        self.message = message
        super().__init__(self.message)

def main(args):
    # user_parameters = {
    #     "region": (args['region'], False, 'us-east-1'),
    # }
    # macaw_config = Configuration('user', args['ROLE'],
    #                        args['config_file'], **user_parameters)
    # region = macaw_config.get_config_setting("region")
    # client_parameters = {
    #     "region": (macaw_config.get_config_setting('region'), False, 'us-east-1'),
    # }
    source_creds = Configuration("credential", args['source'], args['credential_file'], **{"region" : (args['region'], False, 'us-east-1')})
    access_key = source_creds.get_config_setting("aws_access_key_id")
    secret_key = source_creds.get_config_setting("aws_secret_access_key")
    token = source_creds.get_config_setting("aws_session_token")
    expiration = source_creds.get_config_setting("expiration")
    sts_service = AWSSTSService(source_creds.get_config_setting("region"), access_key, secret_key, token)
    validation = arn_validation(args['ROLE'])
    if validation[0]:
        if validation[1]:
            arn = args['ROLE']
        else:
            macaw_config = Configuration('user', args['ROLE'], args['config_file'], **{"region" : (args['region'], False, 'us-east-1')})
            arn = sts_service.generate_arn(macaw_config.get_config_setting("partition"),
                                           macaw_config.get_config_setting("account_number"),
                                           "role", macaw_config.get_config_setting("role_name"),
                                           macaw_config.get_config_setting("path"))
            arn_validation(arn)
    # TODO - update Configuration to handle cases where user passes invalid profile section. Or handle here if all values are None
    # TODO - Add check for credential expiration after adding 'time-left' functionality
    try:
        session_name = sts_service.get_role_session_name()
        assume_role_creds = sts_service.assume_role(arn, session_name, 3600)

        cred_parameters = {
            "region": (sts_service.region, False, 'us-east-1'),
            "output": (None, False, 'json'), #TODO - pull this value in. via config?
            "aws_access_key_id": (assume_role_creds['Credentials']['AccessKeyId'], True, ''),
            "aws_secret_access_key": (assume_role_creds['Credentials']['SecretAccessKey'], True, ''),
            "aws_session_token": (assume_role_creds['Credentials']['SessionToken'], True, ''),
            "expiration": (assume_role_creds['Credentials']['Expiration'], True, '')
        }
        target_creds = Configuration("credential", args['target_profile'], args['credential_file'], **cred_parameters)
        target_creds.write_config()
    except ClientError as err:
        if err.response['Error']['Code'] == "ExpiredToken":
            message = "Session token is expired. Please try running 'macaw-auth login'"
            raise RoleAssumptionError(message)
        else:
            raise err


    # print(source_client["aws_access_key_id"])
    # print(secret_key)
    # print(token)
    # print(expiration)
    

if __name__ == '__main__':
    sys.exit(main())