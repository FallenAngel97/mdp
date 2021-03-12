from fabric import Connection
from fabric.transfer import Transfer
import re
import os
import locale # https://github.com/pyinvoke/invoke/issues/384

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

class SSHInit(object):
    def __init__(self, credentials):
        """

        credentials:
          ip
          user
          password

        """
        self.user = user=credentials[1]
        args = dict(password=credentials[2])
        conn=Connection(host=credentials[0], user=user, port=22, connect_kwargs=args)

        # TODO: Create a ready zip-files, which will be downloaded without the necessity to perform a lot of operations for common distros

        distro_info = conn.run("cat /etc/*-release", hide=True).stdout.strip()
        self.install_os_deps(conn, distro_info)

        conn.close()

        os.makedirs("./.known_machines", exist_ok=True)

        with open(f"./.known_machines/{credentials[0]}.txt", 'a+') as key_file:
            key_file.write("some key")


    def install_os_deps(self, conn, distro_info):

        distro_name = re.search(r"\nNAME=\"(.*)\"", distro_info, re.M).group(1)
        
        if "Ubuntu" in distro_name:
            distro_version = re.search(r"\nDISTRIB_RELEASE=(.*)", distro_info, re.M).group(1)

            conn.sudo("apt-get install python3-pip -y", hide=True)
            transfer = Transfer(conn)
            for file in os.listdir("machine_diagnostics_protocol"):
                if os.path.isdir(f"machine_diagnostics_protocol/{file}"):
                    directoryname = file
                    conn.run(f"mkdir -p {directoryname}")
                    for sub_file in os.listdir(f"machine_diagnostics_protocol/{directoryname}"):
                        transfer.put(
                            f"machine_diagnostics_protocol/{directoryname}/{sub_file}", 
                            f"{directoryname}/"
                        )
                else:
                    transfer.put(f"machine_diagnostics_protocol/{file}")

            if distro_version == "14.04":
                conn.sudo(f"cp /home/{self.user}/mdp.conf /etc/init", hide=True)
                conn.run(f"pip3 install -r /home/{self.user}/requirements.txt --user", hide=True)
                conn.sudo("initctl reload-configuration", hide=True)
                conn.sudo("service mdp restart", hide=True, pty=False)
            else:
                conn.sudo("")
                
        else:
            pass

    @property
    def details(self):
        return [
            self.cpu,
            self.memory
        ]