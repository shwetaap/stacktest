import requests
import token
import os
import ConfigParser
import json

class Network():

    CONFIG_DIR = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config")
    CONFIG_FILE = "testConfig.cfg"
    NETWORK_PORT = ":9696"
    NETWORK_API_VERSION = "/v2.0"
    
    def __init__(self):
	self.config = ConfigParser.ConfigParser()
        self.conf_file = os.path.join(self.CONFIG_DIR, self.CONFIG_FILE)
        self.config.read(self.conf_file)
        self.req_token = token.Token()
        self.token_id = self.req_token.create_token()
        self.req_headers = {'content-type': 'application/json'}
        self.req_headers.update({'X-Auth-Token': self.token_id})
        self.network_name = "net10"
        self.network_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.NETWORK_PORT, self.NETWORK_API_VERSION, '/networks'])
        self.subnet = "10.10.10.0/24"
        self.subnet_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.NETWORK_PORT, self.NETWORK_API_VERSION, '/subnets'])
        self.router_name = "router1"
        self.router_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.NETWORK_PORT, self.NETWORK_API_VERSION, '/routers'])
        

    """ Create network """
    def create_network(self, network_name=None, public_net=False):
	if network_name is None:
	    network_name = self.network_name
	
	if public_net is True:
	    req_data = '{"network": {"name": "' + network_name + '", "router:external": true}}'
	else: 
	    req_data = '{"network": {"name": "' + network_name + '"}}'
	response = requests.post(self.network_url, data=req_data, headers=self.req_headers)
	response_data = json.loads(response.text)
	return response_data

    """ Create subnet"""
    def create_subnet(self, network_name=None, subnet=None, public_net=False, pool_start=None, pool_end=None):
        if network_name is None:
            network_name = self.network_name


        network_id = self.get_network_id(network_name)

        if network_id is None:
	    net_data = self.create_network(network_name=network_name, public_net=public_net)
	    network_id = net_data['network']['id']

	if subnet is None:
	    subnet = self.subnet		
	
	if pool_start and pool_end:
	    req_data = '{"subnet": {"network_id": "' + network_id + '", "ip_version": 4, "cidr": "' + subnet + '", "allocation_pools":[{"start": "' + pool_start + '", ""end": "' + pool_end + '"}]}}'
	else:
	    req_data = '{"subnet": {"network_id": "' + network_id + '", "ip_version": 4, "cidr": "' + subnet + '"}}'

	subnet_resp = requests.post(self.subnet_url, data=req_data, headers=self.req_headers)
	subnet_resp_data = json.loads(subnet_resp.text)
	return subnet_resp_data

    """ Create Router """
    def create_router(self, router_name):
        if router_name is None:
            router_name = self.router_name
            
        req_data = '{"router": {"name": "' + router_name + '"}}'

        router_resp = requests.post(self.router_url, data=req_data , headers=self.req_headers)

        router_resp_data = json.loads(router_resp.text)

        return router_resp_data
    

    """ Add Interface to router """
    def add_interface_router(self, router_name=None, network_name=None, subnet=None):
        if router_name is None:
            router_name = self.router_name
        
        router_id = self.get_router_id(router_name)

        print router_name, router_id

        if router_id is None:
	    router_data = self.create_router(router_name)
	    router_id = router_data['router']['id']

	if network is None:
	    network_name = self.network_name

	if subnet is None:
	    subnet = self.subnet

        subnet_id = self.get_subnet_id(subnet)

        print network_name, subnet, subnet_id
            
        if subnet_id is None:
            subnet_data = self.create_subnet(network_name=network_name, subnet=subnet)
            subnet_id = subnet_data['subnet']['id']
     
	add_interface_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.NETWORK_PORT, self.NETWORK_API_VERSION, '/routers/', router_id, '/add_router_interface'])

        req_data = '{"subnet_id": "' + subnet_id + '"}'

	add_interface_resp = requests.put(add_interface_url, data=req_data, headers=self.req_headers)
	add_interface_data = json.loads(add_interface_resp.text)
	return add_interface_data
        pass

    """ Add Gateway Interface """
    def add_gateway_interface(self, network_name, router_name=None):
	if router_name is None:
	    router_name = self.router_name

	router_id = self.get_router_id(router_name)

	if router_id is None:
            router_data = self.create_router(router_name)
            router_id = router_data['router']['id']

        network_id = self.get_network_id(network_name)

        if network_id is None:
            net_data = self.create_network(network_name=network_name, public_net=True)
            network_id = net_data['network']['id']

	gateway_interface_url = ''.join([self.config.get('AUTHENTICATION', 'URL'), self.NETWORK_PORT, self.NETWORK_API_VERSION, '/routers/', router_id])
	req_data = '{"router": {"external_gateway_info": {"network_id": "' + network_id + '"}}}'

	gateway_interface_resp = requests.put(gateway_interface_url, data=req_data, headers=self.req_headers)
	gateway_interface_data = json.loads(gateway_interface_resp.text)
	return gateway_interface_data


    def get_network_id(self, network_name):
        
        net_resp = requests.get(self.network_url, headers=self.req_headers)
	net_resp_data = json.loads(net_resp.text)
	network_list = net_resp_data['networks']

	network_id = None

        if network_name is not None:
            for net in network_list:
                if net['name'] == network_name:
                    network_id = net['id']
                    break

        return network_id

    def get_subnet_id(self, subnet):

        subnet_resp = requests.get(self.subnet_url, headers=self.req_headers)
	subnet_resp_data = json.loads(subnet_resp.text)
	subnet_list = subnet_resp_data['subnets']

        subnet_id = None

	if subnet is not None:
            for subnetwork in subnet_list:
                if subnetwork['cidr'] == subnet:
                    subnet_id = subnetwork['id']
                    break
        return subnet_id
        

    def get_router_id(self, router_name):

        route_resp = requests.get(self.router_url, headers=self.req_headers)
	route_resp_data = json.loads(route_resp.text)
	router_list = route_resp_data['routers']

	router_id = None

        if router_name is not None:
            for router in router_list:
                if router['name'] == router_name:
                    router_id = router['id']
                    break
        return router_id
"""
#if __name__ == '__main__':
#    network = Network()
    #print "Netoerk Token ID"
    #print network.token_id
#    print network.create_network(network_name="net11", public_net=True)
#    print network.create_subnet(network_name="net14", subnet="10.10.14.0/24")	
#    print network.create_router(router_name="router2")
#    print network.add_interface_router(router_name="router2", network_name="net14", subnet="10.10.14.0/24")
#    print network.network_url, network.req_data, network.response_data
    print token.config.options('AUTHENTICATION')
    print token.config.get('AUTHENTICATION', 'URL')
    token.create_token()
    print token.auth_url, token.admin_tenant_name, token.admin_username, token.admin_password, token.response_data, token.token
"""

"""
Create a token
Create network
Create subnet
Create router
Create public network
Add router interface in a network/gatway interface
Create security groups
Ping
"""
