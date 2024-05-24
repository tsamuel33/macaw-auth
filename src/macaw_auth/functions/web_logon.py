import json
import requests
import sys
import urllib
import webbrowser

from time import sleep

from macaw_auth.classes.configuration import Configuration


def main(args):
    credentials = Configuration("credential", args['PROFILE'], args['credential_file'])
    url_credentials = {}
    url_credentials['sessionId'] = credentials.get_config_setting("aws_access_key_id")
    url_credentials['sessionKey'] = credentials.get_config_setting("aws_secret_access_key")
    url_credentials['sessionToken'] = credentials.get_config_setting("aws_session_token")
    json_string_with_temp_credentials = json.dumps(url_credentials)

    # Get sign-in token from AWS federation endpoint
    request_parameters = "?Action=getSigninToken"
    if sys.version_info[0] < 3:
        def quote_plus_function(s):
            return urllib.quote_plus(s)
    else:
        def quote_plus_function(s):
            return urllib.parse.quote_plus(s)
    request_parameters += "&Session=" + quote_plus_function(json_string_with_temp_credentials)
    # When making a request using credentials for an assumed role, including session duration causes a failure
    request_parameters_no_duration = request_parameters
    request_parameters += "&SessionDuration={}".format(str(args['duration_seconds']))
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    r = requests.get(request_url, verify=args['no_ssl'])
    # Returns a JSON document with a single element named SigninToken.
    try:
        signin_token = json.loads(r.text)
    # If request fails, retry without session duration
    except json.decoder.JSONDecodeError:
        request_url = "https://signin.aws.amazon.com/federation" + request_parameters_no_duration
        r = requests.get(request_url, verify=args['no_ssl'])
        signin_token = json.loads(r.text)

    # Generate sign in URL
    request_parameters = "?Action=login" 
    request_parameters += "&Issuer=Example.org" 
    request_parameters += "&Destination=" + quote_plus_function("https://console.aws.amazon.com/")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    # If a user is already logged in to the console, opening the browser with new
    # credentials will fail. Log out first, then open another window 3 secounds later
    
    # Set logout region
    if args["region"] is not None:
        region = args["region"]
    else:
        region = credentials.get_config_setting("region")
    # Default to us-east-1 if no region is provided.
    if region is None:
        region = "us-east-1"
    # Log out of console to ensure credentials are cleared before logging in
    webbrowser.open_new("https://{}.console.aws.amazon.com/console/logout!doLogout".format(region))
    sleep(3)
    webbrowser.open_new_tab(request_url)