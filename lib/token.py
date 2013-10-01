import json
import requests
import os
import ConfigParser

class Token:
    
    CONFIG_DIR = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config")
    CONFIG_FILE = "testConfig.cfg"
    AUTH_VERSION = "/v2.0"
    AUTH_PORT = ":5000"

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.conf_file = os.path.join(self.CONFIG_DIR, self.CONFIG_FILE)
        self.config.read(self.conf_file)

        

    def create_token(self):
        """ Create Token for authenticating subsequent REST API calls """

        self.auth_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.AUTH_PORT, self.AUTH_VERSION, '/tokens'])
        self.admin_tenant_name = self.config.get('AUTHENTICATION', 'TENANTNAME')
        self.admin_username = self.config.get('AUTHENTICATION', 'USERNAME')
        self.admin_password = self.config.get('AUTHENTICATION', 'PASSWORD')

        req_data = '{"auth":{"passwordCredentials": {"username": "' + self.admin_username + '", "password": "' + self.admin_password + '"}, "tenantName":"' + self.admin_tenant_name + '"}}'
        req_headers = {'content-type': 'application/json'}
        try:
            response = requests.post(self.auth_url, data=req_data, headers=req_headers)
        except requests.ConnectionError, e:
            print e.args
        except requests.HTTPError, e:
            print e.code
        self.response_data = json.loads(response.text)
        self.token = self.response_data['access']['token']['id']
        return self.token
"""
if __name__ == '__main__':
    token = Token()
    print token.conf_file
    print token.config.options('AUTHENTICATION')
    print token.config.get('AUTHENTICATION', 'URL')
    token.create_token()
    print token.auth_url, token.admin_tenant_name, token.admin_username, token.admin_password, token.response_data, token.token
"""
#auth_url = 
