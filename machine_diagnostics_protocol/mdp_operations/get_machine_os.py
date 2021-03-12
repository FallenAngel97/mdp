def subfunc_get_machine_os(self):
    """ Gets machine distribution name """
    from subprocess import Popen, PIPE
    import re
    proc = Popen(["cat /etc/*-release"], stdout=PIPE, shell=True)
    machine_info, err = proc.communicate()
    print("machine info obtained")
    if type(machine_info) == bytes:
        machine_info = machine_info.decode("utf-8")
    print(machine_info)
    distro_name = re.search(r"\nNAME=\"(.*)\"", str(machine_info), re.M).group(1)
    return distro_name
    