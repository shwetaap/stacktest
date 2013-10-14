import requests
import stacktoken
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
        self.req_token = stacktoken.Token()
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

    def create_server(self, server_name, tenant_name=None, network_name=None, subnet=None, image_name=None, flavor_id=None):

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
            self.netobj.create_subnet(network_name=network_name, subnet=subnet)

        # Get Image Id
        image_id = self.imgobj.get_image_id(image_name)
        
        req_data = '{"server": {"flavorRef": "' + flavor_id + '", "imageRef": "' + image_id + '", "name": "' + server_name + '", "networks": [{"uuid": "' + netid + '"}]}}'
        
        
        # Get Tenant Id
        tenant_id = self.get_tenant_id(tenant_name)
        
        server_create_url = ''.join([self.server_url, tenant_id, '/servers'])

        response = requests.post(server_create_url, data=req_data, headers=self.req_headers)
        response_data = json.loads(response.text)
	print response_data
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

    def get_server_id(self, server_name, tenant_id):
    
        server_get_url = ''.join([self.server_url, tenant_id, '/servers'])
        server_resp = requests.get(server_get_url, headers=self.req_headers)
        server_resp_data = json.loads(server_resp.text)
        server_list = server_resp_data['servers']

        server_id = None

        if server_name is not None:
            for server in server_list:
                if server['name'] == server_name:
                    server_id = server['id']
                    break

        return server_id
        

    def get_server_ip(self, server_id, tenant_id, network_name, network_type):
	
	server_get_url = ''.join([self.server_url, tenant_id, '/servers/', server_id])	
	ip_resp = requests.get(server_get_url, headers=self.req_headers)
	ip_resp_data = json.loads(ip_resp.text)
	server_net_list = ip_resp_data['server']['addresses']

        server_ip = None
	
	for net_name in server_net_list:
            if net_name == network_name:
                for net in server_net_list[network_name]:
                    if net['OS-EXT-IPS:type'] == network_type:
                        if net['addr'] is not None:
                            server_ip = net['addr']
                        break
                
            if server_ip is not None:
                break
        
	return server_ip
 	
if __name__ == '__main__':
    compute = Compute()
#    print compute.create_server("test4") 
#    print compute.get_server_ip("cd12d8f9-1fc8-471a-87c2-d5f643eaf9a9", "bccc3685691a4205947dc6d7bc4e532b", "net10")
    tenant_id = compute.get_tenant_id("admin")
    server_id = compute.get_server_id("test3", tenant_id)
    print server_id
    print compute.get_server_ip(server_id, tenant_id, "net10")
    




         
