from .common import arn_validation
from ..classes.configuration import Configuration
from ..classes.sts_saml import AWSSTSService

def main(args):
    validation = arn_validation(args['ROLE'])
    print(validation)

if __name__ == '__main__':
    sys.exit(main())