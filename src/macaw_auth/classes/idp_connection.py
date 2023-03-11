import requests
from requests_ntlm import HttpNtlmAuth #pip install requests-ntlm
from bs4 import BeautifulSoup #pip install beautifulsoup4
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
        self.make_saml_request(self.session)
        if self.auth_type == 'web_form':
            self.create_web_form_payload()
            self.authenticate_to_web_form(self.session)
        self.get_saml_assertion()

    def make_saml_request(self, session):
        session = session
        if self.auth_type == 'ntlm':
            session.auth = HttpNtlmAuth(self.__username, self.__password, session)
            feature = "html.parser"
        elif self.auth_type == 'web_form':
            # feature = "lxml"
            feature = "html.parser"
        else:
            message = "Incorrect authorization type provided. Valid types are 'ntlm' or 'web_form'"
            ##RAISE ERROR - TODO
        self.response = session.get(self.identity_url, verify=self.ssl_verification)
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

    def authenticate_to_web_form(self, session):
        for inputtag in self.__soup.find_all(re.compile('(FORM|form)')):
            action = inputtag.get('action')
            loginid = inputtag.get('id')
            if (action and loginid == "loginForm"):
                parsedurl = urlparse(self.identity_url)
                self._redirect_url = parsedurl.scheme + "://" + parsedurl.netloc + action

        # Performs the submission of the IdP login form with the above post data
        response = session.post(
            self._redirect_url, data=self.__payload, verify=self.ssl_verification)
        self.__soup = BeautifulSoup(response.text, features="html.parser")

    def get_saml_assertion(self):
        assertion = ''

        # Look for the SAMLResponse attribute of the input tag (determined by
        # analyzing the debug print lines above)
        for inputtag in self.__soup.find_all('input'):
            if(inputtag.get('name') == 'SAMLResponse'):
                #print(inputtag.get('value'))
                assertion = inputtag.get('value')

        # Better error handling is required for production use.
        if (assertion == ''):
            #TODO: Insert valid error checking/handling
            print('Response did not contain a valid SAML assertion')
            sys.exit(0)
        self.assertion = assertion

        # Debug only
        # print(base64.b64decode(assertion))