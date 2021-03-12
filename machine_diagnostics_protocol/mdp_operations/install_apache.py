def subfunc_install_apache(self):
    """ Install Apache with default configuration for Ubuntu """
    from subprocess import Popen, PIPE
    password = "vagrant"
    shell_cmd = r'''
#!/bin/bash
echo {0} | sudo apt-get update
echo {0} | sudo apt-get install apache2
echo {0} | sudo ufw allow 80/tcp
    '''.format(password)
    proc = Popen([shell_cmd], stdout=PIPE, shell=True)
    installation_result, err = proc.communicate()
    if type(installation_result) == bytes:
        installation_result = installation_result.decode("utf-8")

    return installation_result

# TODO: create a remove logic
def redo_subfunc_install_apache(self):
    """ Delete Apache from host """
    pass
