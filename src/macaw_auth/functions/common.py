def arn_validation(arn : str, arn_type="role"):
    is_arn = True
    is_valid = True
    message = ""
    if arn_type == "role":
        arn_prefix = "role/"
    elif arn_type == "idp":
        arn_prefix = "saml-provider/"
    arn_split = arn.split(":")
    split_length = len(arn_split)
    if split_length == 1:
        is_arn = False
        message = "Entry is not an ARN"
    else:
        if split_length != 6:
            is_valid = False
            message = "ARN structure is incorrect. Please confirm ARN."
        elif arn_split[0] != "arn":
            is_valid = False
            message = "ARN should start with 'arn"
        elif arn_split[1] not in ['aws', 'aws-cn', 'aws-us-gov']:
            is_valid = False
            message = "ARN partition should be one of 'aws', 'aws-cn', or 'aws-us-gov'"
        elif arn_split[2] != "iam":
            is_valid = False
            message = "AWS service in ARN should be 'iam'"
        elif arn_split[3] != '':
            is_valid = False
            message = "ARN should have '::' between service and account number"
        elif not arn_split[5].startswith(arn_prefix):
            is_valid = False
            message = "ARN of type '{}' should have '{}' before the resource path and name".format(arn_type, arn_prefix)
        elif arn_type == "idp" and len(arn_split[5].split("/")) > 2:
            is_valid = False
            message = "IdP name should not have '/'. Ensure you have not included a path."
        else:
            account = arn_split[4]
            try:
                int(account)
                if len(account) != 12:
                    is_valid = False
                    message = "AWS account number must be 12 digits"
            except ValueError:
                is_valid = False
                message = "AWS account number must be a valid number"
                return (is_arn, is_valid, message)
    return (is_arn, is_valid, message)