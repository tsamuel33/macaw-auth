import sys

from botocore.exceptions import ClientError

from macaw_auth.functions.common import arn_validation
from macaw_auth.classes.configuration import Configuration
from macaw_auth.classes.sts_saml import AWSSTSService


def main(args):
    source_creds = Configuration("credential", args['source'], args['credential_file'],
                                **{"region" : (args['region'], False, 'us-east-1')})
    sts_service = AWSSTSService(source_creds.get_config_setting("region"),
                                source_creds.get_config_setting("aws_access_key_id"),
                                source_creds.get_config_setting("aws_secret_access_key"),
                                source_creds.get_config_setting("aws_session_token"),
                                args['no_ssl'])
    validation = arn_validation(args['ROLE'])
    if validation[0]:
        if validation[1]:
            arn = args['ROLE']
        else:
            macaw_config = Configuration('user', args['ROLE'], args['config_file'],
                                        **{"region" : (args['region'], False, 'us-east-1')})
            arn = sts_service.generate_arn(macaw_config.get_config_setting("partition"),
                                           macaw_config.get_config_setting("account_number"),
                                           "role", macaw_config.get_config_setting("role_name"),
                                           macaw_config.get_config_setting("path"))
            arn_validation(arn)
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
            print("ERROR: Session token is expired. Please try running 'macaw-auth login'")
            sys.exit()
        else:
            raise err

if __name__ == '__main__':
    sys.exit(main())