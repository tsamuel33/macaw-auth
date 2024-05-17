from macaw_auth.functions.common import arn_validation
from macaw_auth.classes.configuration import Configuration
from macaw_auth.classes.sts_saml import AWSSTSService

def main(args):
    validation = arn_validation(args['ROLE'])
    print(validation)

if __name__ == '__main__':
    sys.exit(main())