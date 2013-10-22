import unittest
import stacktoken
import compute
import paramiko
import ConfigParser
import os
import network
import time

class TestInstanceConnectivity(unittest.TestCase):

    CONFIG_DIR = os.path.join((os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "config")
    CONFIG_FILE = "testConfig.cfg"

    "create instance"
    def setUp(self):
        self.config = ConfigParser.ConfigParser()
        self.conf_file = os.path.join(self.CONFIG_DIR, self.CONFIG_FILE)
        self.config.read(self.conf_file)
        self.compute_obj = compute.Compute()
        self.net_obj = network.Network()
        self.first_server = "test1"
        self.second_server = "test2"
        self.third_server = "test3"
        self.fourth_server = "test4"
        self.fifth_server = "test5"
        self.first_tenant = "admin"
        self.second_tenant = "demo"
        self.first_network = "net10"
        self.second_network = "net11"
        self.third_network = "net12"
	self.first_subnet = "10.10.10.0/24"
        self.first_network_gw = "10.10.10.1"
	self.second_subnet = "10.10.11.0/24"
        self.second_network_gw = "10.10.11.1"
	self.third_subnet = "10.10.12.0/24"
        self.third_network_gw = "10.10.12.1"
        self.image_name = "cirros-x86_64"
        self.public_net_name = "nova"
	self.router_name = "router1"
        self.public_subnet = self.config.get('EXTERNAL_NETWORK', 'FLOATING_IP')
        self.pool_start = self.config.get('EXTERNAL_NETWORK', 'FLOATING_IP_POOL_START')
        self.pool_end = self.config.get('EXTERNAL_NETWORK', 'FLOATING_IP_POOL_END')
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.username = "cirros"
        self.password = "cubswin:)"

    def get_floating_ip(self, server_ip, server_id, tenant_id, net_name, net_type):
	server_float_ip = None
	server_float_ip = self.compute_obj.get_server_ip(server_id, tenant_id,
							 net_name, net_type)
	if server_float_ip is None:
	    public_netid = self.net_obj.get_network_id(self.public_net_name)
	    if public_netid is None:
		self.net_obj.create_network(network_name=self.public_net_name,
					    public_net=True)
                self.net_obj.create_subnet(network_name=self.public_net_name,
                                           subnet=self.public_subnet,
                                           public_net=True,
                                           pool_start=self.pool_start,
                                           pool_end=self.pool_end)
                public_netid = self.net_obj.get_network_id(self.public_net_name)
	    
	    instance_port_id = self.net_obj.get_port_id(server_id, server_ip)
	    self.net_obj.associate_floating_ip(instance_port_id, public_netid)
	    server_float_ip = self.compute_obj.get_server_ip(server_id, tenant_id,
                                                             net_name, net_type)

        return server_float_ip

    def add_router_gateway(self, network_name, subnet, subnet_pool_start,
                           subnet_pool_end, router_name):
        
        # if gateway interface exists of router do nothing 
        # if it does add the gateway for the given public network
        router_id = self.net_obj.get_router_id(router_name)
        if router_id is not None:
            if self.net_obj.check_router_gateway_exists(router_id) is True:
                pass
            else:
                self.net_obj.add_gateway_interface(network_name=network_name, subnet=subnet,
                                                   subnet_pool_start=subnet_pool_start,
                                                   subnet_pool_end=subnet_pool_end,
                                                   router_name=router_name)
        if router_id is None:
            self.net_obj.add_gateway_interface(network_name=network_name, subnet=subnet,
                                                   subnet_pool_start=subnet_pool_start,
                                                   subnet_pool_end=subnet_pool_end,
                                                   router_name=router_name)
 
    def add_router_interface(self, router_name, network_name=None,
                            subnet=None, network_gw=None):
        
        # if gateway interface exists of router do nothing 
        # if it does add the gateway for the given public network
        router_id = self.net_obj.get_router_id(router_name)
        if router_id is not None:
            if self.net_obj.get_port_id(router_id, network_gw) is not None:
                pass
            else:
                self.net_obj.add_interface_router(router_name=router_name,
                                                  network_name=network_name,
                                                  subnet=subnet)
         
		
    "test instance connectivity in the same network"
    def test_vm_connectivity_same_network(self):
        # Extract Floating Ip and private Ip of the first server
	first_tenant_id = None
	first_server_id = None
        first_tenant_id = self.compute_obj.get_tenant_id(self.first_tenant)
        first_server_id = self.compute_obj.get_server_id(self.first_server,
                                                         first_tenant_id)
	if first_server_id is None:
	    self.compute_obj.create_server(self.first_server,
                                           tenant_name=self.first_tenant,
                                           network_name=self.first_network,
                                           subnet=self.first_subnet,
                                           image_name=self.image_name)
	    time.sleep(10)
	    first_server_id = self.compute_obj.get_server_id(self.first_server,
                                                             first_tenant_id)

        first_server_ip = self.compute_obj.get_server_ip(first_server_id,
                                                         first_tenant_id,
                                                         self.first_network,
                                                         "fixed")
 
        # Extract private Ip of the second server
	second_server_id = None
	second_server_id = self.compute_obj.get_server_id(self.second_server,
                                                          first_tenant_id)
	if second_server_id is None:
	    self.compute_obj.create_server(self.second_server,
                                           tenant_name=self.first_tenant,
                                           network_name=self.first_network,
                                           subnet=self.first_subnet,
                                           image_name=self.image_name)
	    time.sleep(10)
	    second_server_id = self.compute_obj.get_server_id(self.second_server,
                                                              first_tenant_id)

        second_server_ip = self.compute_obj.get_server_ip(second_server_id,
                                                          first_tenant_id,
                                                          self.first_network,
                                                          "fixed")

        # Create router and assign the gateway for the router to an external network
        self.add_router_gateway(self.public_net_name, self.public_subnet,
                                self.pool_start, self.pool_end,
				self.router_name)

        #Place a router interface in the private network
        self.add_router_interface(self.router_name, self.first_network,
                                  self.first_subnet, self.first_network_gw)

        # Get floating ip for first server
        first_server_float_ip = self.get_floating_ip(first_server_ip,
                                                     first_server_id,
                                                     first_tenant_id,
                                                     self.first_network,
                                                     "floating")

        second_server_float_ip = self.get_floating_ip(second_server_ip,
                                                     second_server_id,
                                                     first_tenant_id,
                                                     self.first_network,
                                                     "floating")

        cmd = "ping -c 5 " + second_server_ip
	print first_server_float_ip, self.username, self.password
        time.sleep(60)
        self.ssh.connect(first_server_float_ip, username=self.username,
                         password=self.password)
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
	print stderr.channel.recv_exit_status()
	self.assertEqual(stderr.channel.recv_exit_status(), 0)

        

    "connectivity between instances in different networks same tenant"
    def test_vm_connectivity_different_network_same_tenant(self):
        # Extract Floating Ip and private Ip of the first server
	first_tenant_id = None
        first_server_id = None
        first_tenant_id = self.compute_obj.get_tenant_id(self.first_tenant)
        first_server_id = self.compute_obj.get_server_id(self.first_server,
                                                         first_tenant_id)
	if first_server_id is None:
            self.compute_obj.create_server(self.first_server,
                                           tenant_name=self.first_tenant,
                                           network_name=self.first_network,
                                           subnet=self.first_subnet,
                                           image_name=self.image_name)
	    time.sleep(10)
            first_server_id = self.compute_obj.get_server_id(self.first_server,
                                                             first_tenant_id)


        first_server_ip = self.compute_obj.get_server_ip(first_server_id,
                                                         first_tenant_id,
                                                         self.first_network,
                                                         "fixed")

        # Extract private Ip of the second server
        second_server_id = None
        second_server_id = self.compute_obj.get_server_id(self.third_server,
                                                          first_tenant_id)
        if second_server_id is None:
            self.compute_obj.create_server(self.third_server,
                                           tenant_name=self.first_tenant,
                                           network_name=self.second_network,
                                           subnet=self.second_subnet,
                                           image_name=self.image_name)
	    time.sleep(10)
            second_server_id = self.compute_obj.get_server_id(self.third_server,
                                                              first_tenant_id)
	
        second_server_ip = self.compute_obj.get_server_ip(second_server_id,
                                                          first_tenant_id,
                                                          self.second_network,
                                                          "fixed")

        # Create router and assign the gateway for the router to an external network
        self.add_router_gateway(self.public_net_name, self.public_subnet,
                                self.pool_start, self.pool_end,
                                self.router_name)

        #Place a router interface in the private network
        self.add_router_interface(self.router_name, self.first_network,
                                  self.first_subnet, self.first_network_gw)
	self.net_obj.add_interface_router(router_name=self.router_name,
                                          network_name=self.second_network,
                                          subnet=self.second_subnet)

        # Get floating ip for first server
        first_server_float_ip = self.get_floating_ip(first_server_ip,
                                                     first_server_id,
                                                     first_tenant_id,
                                                     self.first_network,
                                                     "floating")

        second_server_float_ip = self.get_floating_ip(second_server_ip,
                                                     second_server_id,
                                                     first_tenant_id,
                                                     self.second_network,
                                                     "floating")
        
        cmd = "ping -c 5 " + second_server_ip
        time.sleep(60)
	self.ssh.connect(first_server_float_ip, username=self.username,
                         password=self.password)
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
#	self.assertNotEqual(stderr.channel.recv_exit_status(), 0)


#	stdin, stdout, stderr = self.ssh.exec_command(cmd)
        self.assertEqual(stderr.channel.recv_exit_status(), 0)
    "connectivity between instance in shared network different tenants"

    "connectovity between instances in different networks different tenat"

    "multiple network connectivity"

    "floating ip association"

    "duplicate private subnet creation"

    "quantum router deletion error until interfaces removed"

    "subnet used up"

    

