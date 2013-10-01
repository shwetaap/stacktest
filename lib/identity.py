import requests
import token
import os
import ConfigParser
import json

class Image():
    
    CONFIG_DIR = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config")
    CONFIG_FILE = "testConfig.cfg"
    IDENTITY_PORT = ":5000"
    IDENTITY_API_VERSION = "/v2.0" 

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.conf_file = os.path.join(self.CONFIG_DIR, self.CONFIG_FILE)
        self.config.read(self.conf_file)
        self.req_token = token.Token()
        self.token_id = self.req_token.create_token()
        self.req_headers = {'content-type': 'application/json'}
        self.req_headers.update({'X-Auth-Token': self.token_id})
        self.image_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.IMAGE_PORT, self.IMAGE_API_VERSION, '/images'])
        self.image_name = "cirros-x86_64"

    def get_image_id(self, image_name):

        img_resp = requests.get(self.image_url, headers=self.req_headers)
        img_resp_data = json.loads(img_resp.text)
        image_list = img_resp_data['images']

        image_id = None

        if image_name is not None:
            for img in image_list:
                if img['name'] == image_name:
                    image_id = img['id']
                    break

        return image_id  
