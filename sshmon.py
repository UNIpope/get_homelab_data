from nornir.plugins.functions.text import print_result
import json
import spur
from nornir import InitNornir

nr = InitNornir(core={'num_workers': 2})
print(nr.inventory.hosts)

def get_data(task):
    result = {}
    shell = spur.SshShell(hostname=task.host.name, username=task.host.username, password=task.host.password)

    with shell:
        if "pi" in task.host.groups:
            result["temp"] = float(shell.run(["vcgencmd", "measure_temp"]).output.decode("utf-8").strip().replace("temp=","")[:-2])

        #storage use
        rootfs = shell.run(["df"]).output.decode("utf-8").split("\n")[1].split()
        if rootfs[5] == "/":
            result["fsused"] = int(rootfs[2])/ 1e+6
            result["fs"] = rootfs[4]
            
        #memory
        meminfo = list(map(shell.run(["cat","/proc/meminfo"]).output.decode("utf-8").split("\n").__getitem__, [0,1,2]))
        result["memused"] =  (int(meminfo[0].split()[1]) - int(meminfo[2].split()[1])) / 1e+6
        result["mem"] =  str(result["memused"] / (int(meminfo[0].split()[1]) / 1e+6) * 100)[:4] + "%"

        #cpu
        vmstat = shell.run(["vmstat"]).output.decode("utf-8")
        vmstato = list(map(vmstat.split("\n")[2].split().__getitem__, [13, 14]))

        result["cpuidle"] = int(vmstato[1])
        result["cpuuse"] = int(vmstato[0])

    return result

def pushdb():
    pass

#run against all
v = nr.run(task=get_data, num_workers=1)
print_result(v)
