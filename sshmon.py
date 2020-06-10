from nornir.plugins.functions.text import print_result
import json
import spur
from nornir import InitNornir

nr = InitNornir(core={'num_workers': 2})
print(nr.inventory.hosts)

def get_data_vms(task):
    result = {}
    shell = spur.SshShell(hostname=task.host.name, username=task.host.username, password=task.host.password)

    with shell:
        #cpu and mem
        vmstat = shell.run(["vmstat"]).output.decode("utf-8")
        vmstato = list(map(vmstat.split("\n")[2].split().__getitem__, [4, 5, 13, 14]))

        result["cpuidle"] = int(vmstato[3])
        result["cpuus"] = int(vmstato[2])
        result["cache"] = float(vmstato[1]) / 1e+6
        result["buff"] = float(vmstato[0]) / 1e+6


    return result

def get_data_pi(task):
    result = {}
    shell = spur.SshShell(hostname=task.host.name, username=task.host.username, password=task.host.password)

    with shell:
        result["temp"] = float(shell.run(["vcgencmd", "measure_temp"]).output.decode("utf-8").strip().replace("temp=","")[:-2])

        #cpu and mem
        vmstat = shell.run(["vmstat"]).output.decode("utf-8")
        vmstato = list(map(vmstat.split("\n")[2].split().__getitem__, [4, 5, 13, 14]))

        result["cpuidle"] = int(vmstato[3])
        result["cpuus"] = int(vmstato[2])
        result["cache"] = float(vmstato[1]) / 1e+6
        result["buff"] = float(vmstato[0]) / 1e+6
        
    return result

r = nr.run(task=get_data_pi, num_workers=1)
print_result(r)

"""
pi_hosts = nr.filter(groups="pi")
print(pi_hosts)
res = pi_hosts.run(task=get_temp, num_workers=2)
print(res)
print_result(res, vars=["stdout"])
"""