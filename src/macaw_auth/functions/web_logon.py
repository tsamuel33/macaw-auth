import webbrowser

from macaw_auth.classes.configuration import Configuration

import urllib, json, sys
import requests


def main(args):
    credentials = Configuration("credential", args['PROFILE'], args['credential_file'])
    url_credentials = {}
    url_credentials['sessionId'] = credentials.get_config_setting("aws_access_key_id")
    url_credentials['sessionKey'] = credentials.get_config_setting("aws_secret_access_key")
    url_credentials['sessionToken'] = credentials.get_config_setting("aws_session_token")
    json_string_with_temp_credentials = json.dumps(url_credentials)

    # Get sign-in token from AWS federation endpoint
    request_parameters = "?Action=getSigninToken"
    request_parameters += "&SessionDuration=43200"
    if sys.version_info[0] < 3:
        def quote_plus_function(s):
            return urllib.quote_plus(s)
    else:
        def quote_plus_function(s):
            return urllib.parse.quote_plus(s)
    request_parameters += "&Session=" + quote_plus_function(json_string_with_temp_credentials)
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    r = requests.get(request_url, verify=args['no_ssl'])
    # Returns a JSON document with a single element named SigninToken.
    signin_token = json.loads(r.text)

    # Generate sign in URL
    request_parameters = "?Action=login" 
    request_parameters += "&Issuer=Example.org" 
    request_parameters += "&Destination=" + quote_plus_function("https://console.aws.amazon.com/")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    # Open the URL
    webbrowser.open_new(request_url)

    #TODO - If you're already logged in, the process doesn't switch over
    #TODO - Troubleshoot why assumed role browser sessions error out