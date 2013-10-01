import requests
import token
import os
import ConfigParser
import json
import network
import image

class Compute():
    
    CONFIG_DIR = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config")
    CONFIG_FILE = "testConfig.cfg"
    COMPUTE_PORT = ":8774"
    COMPUTE_API_VERSION = "/v2/"
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
        self.tenant_name = "admin"
        self.network_name = "net10"
        self.image_name = "cirros-x86_64"
        self.flavor_id = "1"
        self.netobj = network.Network()
        self.server_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.COMPUTE_PORT, self.COMPUTE_API_VERSION])
        self.imgobj = image.Image()
        self.identity_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.IDENTITY_PORT, self.IDENTITY_API_VERSION, '/tenants'])

    def create_server(self, server_name, tenant_name=None, network_name=None, image_name=None, flavor_id=None):

        if tenant_name is None:
            tenant_name = self.tenant_name
              
        if network_name is None:
            network_name = self.network_name

        if image_name is None:
            image_name = self.image_name

        if flavor_id is None:
            flavor_id = self.flavor_id

        netid = self.netobj.get_network_id(network_name)

        if netid is None:
            new_net = self.netobj.create_network(network_name=network_name)
            netid = new_net['network']['id']

        # Get Image Id
        image_id = self.imgobj.get_image_id(image_name)
        
        req_data = '{"server": {"flavorRef": "' + flavor_id + '", "imageRef": "' + image_id + '", "name": "' + server_name + '", "networks": [{"uuid": "' + netid + '"}]}}'
        
        
        # Get Tenant Id
        tenant_id = self.get_tenant_id(tenant_name)
        
        server_create_url = ''.join([self.server_url, tenant_id, '/servers'])

        response = requests.post(server_create_url, data=req_data, headers=self.req_headers)
        response_data = json.loads(response.text)
        return response_data

    def get_tenant_id(self, tenant_name):

        id_resp = requests.get(self.identity_url, headers=self.req_headers)
        id_resp_data = json.loads(id_resp.text)
        tenant_list = id_resp_data['tenants']

        tenant_id = None

        if tenant_name is not None:
            for tenant in tenant_list:
                if tenant['name'] == tenant_name:
                    tenant_id = tenant['id']
                    break

        return tenant_id

    
