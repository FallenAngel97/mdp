import socket
import string
import random
import json

from MDPMachineOps import MDPMachineOps

class MDPServer():

    def random_string(self,length):
        pool = string.ascii_letters + string.digits
        return ''.join(random.choice(pool) for i in range(length))

    def __init__(self, server_ip = "0.0.0.0", server_port = 12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((server_ip, server_port))
        self.should_show_key = False
        with open("key.txt", 'a+') as key_file:
            key_file.seek(0)
            first_char = key_file.read(1)
            if not first_char:
                uniq_hash = self.random_string(16)
                key_file.write(uniq_hash)
                self.private_key = uniq_hash
                self.should_show_key = True
            else:
                key_file.seek(0)
                self.private_key = key_file.readline()

    def start_server(self):
        print("Started server")

        while True:
            client_ip, request_data = self.get_client_data()
            
            print("Message\n" + str(request_data) + "\nFrom:\n" + str(client_ip))

            request_serialized = json.loads(request_data.decode("utf-8"))

            data_to_transmit = {
                'status': request_serialized["key"] == self.private_key
            }

            if(data_to_transmit['status'] and 'operations' in request_serialized):
                self.should_show_key = False
                mdp_machine_ops = MDPMachineOps()
                for operation in request_serialized['operations']:
                    data_to_transmit[operation] = mdp_machine_ops.do_op(operation)

            if(self.should_show_key):
                data_to_transmit['machine_key'] = self.private_key

            print("The answer:" + json.dumps(data_to_transmit))

            self.send_msg(json.dumps(data_to_transmit), client_ip)


    def send_msg(self, msg, ip_address: str):
        self.sock.sendto(str(msg).encode(), ip_address)

    def get_client_data(self):
        request_data, address = self.sock.recvfrom(1024)
        return (address, request_data)

    def set_machines_in_cluster(self, machines):
        # TODO: replace with actual logic
        with open("machines.yml", "a+") as machines_file:
            machines_file.write("192.168.33.10")

    def create_backup_cluster(self):
        self.cluster_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cluster_socket.bind(('0.0.0.0', 144001))
        