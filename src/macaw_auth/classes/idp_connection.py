import requests
from requests_ntlm import HttpNtlmAuth #pip install requests-ntlm
from bs4 import BeautifulSoup #pip install beautifulsoup4
from getpass import getpass
from urllib.parse import urlparse
import re
import sys
import base64

class SAMLAssertion:

    def __init__(self, username, password, identity_url, auth_type, ssl_verification=True):
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
        if self.auth_type == 'ntlm':
            self.session.auth = HttpNtlmAuth(self.__username, self.__password, self.session)
            feature = "html.parser"
        elif self.auth_type == 'web_form':
            # feature = "lxml"
            feature = "html.parser"
        else:
            message = "Incorrect authorization type provided. Valid types are 'ntlm' or 'web_form'"
            ##RAISE ERROR - TODO
        self.response = self.session.get(self.identity_url, verify=self.ssl_verification)
        self._redirect_url = self.response.url
        self.__soup = BeautifulSoup(self.response.text, features=feature)

        # formsoup = BeautifulSoup(response.text, features="lxml")
        # payload = {}

    def create_web_form_payload(self):
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
        mfa_enabled = False
        assertion = ''

        # Look for the SAMLResponse attribute of the input tag (determined by
        # analyzing the debug print lines above)
        for inputtag in self.__soup.find_all('input'):
            if(inputtag.get('name') == 'SAMLResponse'):
                #print(inputtag.get('value'))
                assertion = inputtag.get('value')
                break
            if('vip' in inputtag.get('name')):
                mfa_enabled = True

        if (assertion == ''):
            invalid_assertion = True
            if mfa_enabled:
                self.authenticate_with_mfa()
                for inputtag in self.__soup.find_all('input'):
                    if(inputtag.get('name') == 'SAMLResponse'):
                        assertion = inputtag.get('value')
                        invalid_assertion = False
                        break
            if invalid_assertion:
                #TODO: Insert valid error checking/handling
                print('Response did not contain a valid SAML assertion')
                sys.exit(0)
        self.assertion = assertion

        # Debug only
        # print(base64.b64decode(assertion))

    def get_vip_code(self):
        self.__vipcode = getpass(prompt='Enter your Symantec VIP security code: ')
        try:
            int(self.__vipcode)
        except ValueError as err:
            print('ERROR: Code must be a number. Try again...')
            self.get_vip_code()

    def authenticate_with_mfa(self):
        self.get_vip_code()
        payload = {}

        for inputtag in self.__soup.find_all('input'):
            name = inputtag.get('name','')
            value = inputtag.get('value','')
            # Locate VIP code fields in web form by searching for "[security_]code"
            if "code" in name.lower():
                payload[name] = self.__vipcode
            else:
                # Keep existing value
                payload[name] = value

        # Performs the submission of the Symantec VIP code
        response = self.session.post(
            self._redirect_url, data=payload, verify=self.ssl_verification)
        self.__soup = BeautifulSoup(response.text, features="html.parser")