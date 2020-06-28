from nornir.plugins.functions.text import print_result
import json, re, spur
from nornir import InitNornir
from pprint import pprint

def push_db(client, json_body):
    try:
        client.switch_database('server')
        client.write_points(json_body)
    except:
        print("error: writing to database")

def create_body(nout):
    json_body = []
    for host in nout:
        json_body.append({"measurement": host[:-4], "fields": nout[host][0].result})

    return json_body

def get_data(task):
    result = {}
    shell = spur.SshShell(hostname=task.host.name, username=task.host.username, password=task.host.password)

    with shell:
        #rasbrry pi commands
        if "pi" in task.host.groups:
            result["temp"] = float(shell.run(["vcgencmd", "measure_temp"]).output.decode("utf-8").strip().replace("temp=","")[:-2])

        #hypervisor commands
        if "host" in task.host.groups:
            # zfs filesys check
            zpool = shell.run(["zpool", "status"]).output.decode("utf-8").split("\n")[6:-3]
            zpool = [re.sub(' +', ': ', i.replace("\t"," "))[2:-9] for i in zpool]
            print(zpool)
            
            zpoolo = {}
            for i in zpool:
                l = i.split(": ")
                result["zfs-"+l[0]] = l[1]

            blk = json.loads(shell.run(["lsblk", "--json"]).output.decode("utf-8"))
            drives = []            
            for drive in blk["blockdevices"]:
                if "sd" in drive["name"]:
                    drives.append(drive["name"])

            for drive in drives:
                dtemp = shell.run(["hddtemp", "/dev/{}".format(drive)]).output.decode("utf-8").strip().split(": ")
                result[dtemp[0][-3:]] = dtemp[2]


        #commands for all devices
        #storage use
        rootfs = shell.run(["df"]).output.decode("utf-8").split("\n")[1].split()
        if rootfs[5] == "/":
            result["fsused"] = int(rootfs[2])/ 1e+6
            result["fs"] = rootfs[4][:-1]
            
        #memory
        meminfo = list(map(shell.run(["cat","/proc/meminfo"]).output.decode("utf-8").split("\n").__getitem__, [0,1,2]))
        result["memused"] =  (int(meminfo[0].split()[1]) - int(meminfo[2].split()[1])) / 1e+6
        result["mem"] =  str(result["memused"] / (int(meminfo[0].split()[1]) / 1e+6) * 100)[:4]

        #cpu
        vmstat = shell.run(["vmstat"]).output.decode("utf-8")
        vmstato = list(map(vmstat.split("\n")[2].split().__getitem__, [13, 14]))

        result["cpuidle"] = int(vmstato[1])
        result["cpuuse"] = int(vmstato[0])

    return result

def run_nor(client):
    #run nornir + spur
    nr = InitNornir(core={'num_workers': 6})
    nout = nr.run(task=get_data)

    #format + send to database
    json_body = create_body(nout)
    pprint(json_body)
    #push_db(client, json_body)

if __name__ == "__main__":
    from influxdb import InfluxDBClient
    client = InfluxDBClient(host='monpi.lan', port=8086)
    run_nor(client)
