import requests
from requests_ntlm import HttpNtlmAuth #pip install requests-ntlm
from bs4 import BeautifulSoup #pip install beautifulsoup4
from getpass import getpass
from urllib.parse import urlparse
import re

class AuthenticationError(Exception):
    """
    Raises an exception when the user is unable to successfully
    authenticate.

    Attributes:
        message (str): message indicating the specifics of the error
    """

    def __init__(self,
            message='Authentication response did not contain a valid' \
                    ' SAML assertion. Please check your credentials.'):
        self.message = message
        super().__init__(self.message)

class SAMLAssertion:
    """
    Makes authentication request to identity provider and returns
    the SAML Assertation response.

    Arguments:
        username (str): The username used to log in
        password (str): The user's password
        identity_url (str): The URL to authenticate to
        auth_type (str): The type of authentication request that will
            be attempted (ntlm | web_form)
        ssl_verification (bool): Whether the SSL certificate of the STS
            endpoint should be verified
    """

    def __init__(self, username, password, identity_url, auth_type, ssl_verification=True):
        """
        Constructs the attributes of the SAMLAssertion object
        
        Attributes:
            identity_url (str): The URL to authenticate to
            ssl_verification (bool): Whether the SSL certificate of the
                STS endpoint should be verified
            auth_type (str): The type of authentication request that
                will be attempted (ntlm | web_form)
            session (requests.Session): The authenticated session
            assertion (XML): The SAML assertion
        """

        self.identity_url = identity_url
        self.ssl_verification = ssl_verification
        self.auth_type = auth_type
        self.__username = username
        self.__password = password
        self.session = requests.Session()
        self.make_saml_request()
        if self.auth_type == 'web_form':
            self.create_web_form_payload()
            self.authenticate_to_web_form()
        self.get_saml_assertion()

    def make_saml_request(self):
        """
        Makes SAML authentication request
        """

        if self.auth_type == 'ntlm':
            self.session.auth = HttpNtlmAuth(self.__username, self.__password, self.session)
        self.response = self.session.get(self.identity_url, verify=self.ssl_verification)
        print(self.response.text)
        if self.auth_type == 'web_form':
            self._redirect_url = self.response.url
        self.__soup = BeautifulSoup(self.response.text, features="html.parser")

    def create_web_form_payload(self):
        """
        Creates required payload for web form SAML requests
         """

        payload = {}

        for inputtag in self.__soup.find_all(re.compile('(INPUT|input)')):
            name = inputtag.get('name','')
            value = inputtag.get('value','')
            # Locate user credential fields in web form by searching for "user[name]", "email", and "pass[word]"
            if "user" in name.lower():
                payload[name] = self.__username
            elif "email" in name.lower():
                payload[name] = self.__username
            elif "pass" in name.lower():
                payload[name] = self.__password
            else:
                # Keep existing value
                payload[name] = value

        self.__payload = payload

    def authenticate_to_web_form(self):
        """
        Makes SAML authentication requests for web form authentication
        """

        for inputtag in self.__soup.find_all(re.compile('(FORM|form)')):
            action = inputtag.get('action')
            loginid = inputtag.get('id')
            if (action and loginid == "loginForm"):
                parsedurl = urlparse(self.identity_url)
                self._redirect_url = parsedurl.scheme + "://" + parsedurl.netloc + action

        # Performs the submission of the IdP login form with the above post data
        response = self.session.post(
            self._redirect_url, data=self.__payload, verify=self.ssl_verification)
        self.__soup = BeautifulSoup(response.text, features="html.parser")

    def get_saml_assertion(self):
        """
        Makes request to retrieve SAML assertion


        """

        mfa_enabled = False
        assertion = ''

        # Look for the SAMLResponse attribute of the input tag (determined by
        # analyzing the debug print lines above)
        for inputtag in self.__soup.find_all('input'):
            if(inputtag.get('name') == 'SAMLResponse'):
                assertion = inputtag.get('value')
                break
            if('vip' in inputtag.get('name')):
                mfa_enabled = True

        if (assertion == ''):
            invalid_assertion = True
            if mfa_enabled:
                assertion = self.authenticate_with_mfa()
            else:
                message = "Authentication attempt did not contain a valid SAML assertion. Please confirm credentials and network connectivity."
                raise AuthenticationError(message)
        self.assertion = assertion

    def get_vip_code(self):
        """
        Gets code required for user to log in with Symantec VIP
        """

        vip_code = getpass(prompt='Enter your Symantec VIP security code: ')
        try:
            int(vip_code)
            return vip_code
        except ValueError as err:
            print('ERROR: Code must be a number. Try again...')
            self.get_vip_code()

    def authenticate_with_mfa(self, attempt=0):
        """
        Makes authentication attempt using MFA code
        """

        current_attempt = attempt + 1
        # Attempt to authenticate with MFA up to 3 times
        if current_attempt <= 3:
            invalid_assertion = True
            code = self.get_vip_code()
            payload = {}

            for inputtag in self.__soup.find_all('input'):
                name = inputtag.get('name','')
                value = inputtag.get('value','')
                # Locate VIP code fields in web form by searching for "[security_]code"
                if "code" in name.lower():
                    payload[name] = code
                else:
                    # Keep existing value
                    payload[name] = value

            # Performs the submission of the Symantec VIP code
            response = self.session.post(
                self._redirect_url, data=payload, verify=self.ssl_verification)
            self.__soup = BeautifulSoup(response.text, features="html.parser")
            for inputtag in self.__soup.find_all('input'):
                if(inputtag.get('name') == 'SAMLResponse'):
                    assertion = inputtag.get('value')
                    invalid_assertion = False
                    break
            if invalid_assertion:
                print("Incorrect code. Try again... (Strike {}!)".format(str(current_attempt)))
                self.authenticate_with_mfa(current_attempt)
            else:
                return assertion
        else:
            # Error out if user enters MFA code incorrectly 3 times
            message = "Sorry, you struck out. Aborting login...".format(str(attempt))
            raise AuthenticationError(message)