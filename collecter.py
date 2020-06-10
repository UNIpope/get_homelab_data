from influxdb import InfluxDBClient
import requests
import sched, time
import subprocess
import json 


"""
Run speedtest command and parse results.

Selects best server based on ping.
--json : Speeds listed in bit/s and not affected by --bytes.
"""
def speed():
    command = ['speedtest', '--json']
    process = subprocess.Popen(command,stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

    ocode = process.wait()

    try:
        output = json.loads(process.stdout.read())
        
        return {"down": round(output["download"]/1000000),
                "up":  round(output["upload"]/1000000),
                "ping": output["ping"]
                }
    except:
        return {"down": 0,
                "up":  0,
                "ping": 0
                }

#Ping google and checks for any packet loss
def ping():
    command = ['ping', "-c", '1', "google.com"]
    process = subprocess.Popen(command,stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

    ocode = process.wait()
    output = process.stdout.read()

    if " 0% packet loss" in output:
        pingStatus = 1
    else:
        pingStatus = 0

    return pingStatus

"""
Parse api.php page from pihole dns server.
Drop un-used values
Gravity is the list of blocked domains.
hours = epoch seconds / 3600
"""
def pihole():
    api = requests.get("http://netpi.lan/admin/api.php")
    API_out = api.json()

    keep = ['dns_queries_today', 'ads_percentage_today', 'ads_blocked_today', 'unique_clients', 'unique_domains','domains_being_blocked']
    d = dict((k, v) for (k, v) in API_out.iteritems() if k in keep)
    
    epoch_time = int(time.time())
    d["gravup"] = (epoch_time - API_out["gravity_last_updated"]["absolute"])/3600
    
    return d

"""
get/write to database every 15 seconds
"""
def ctrlp(client):
    o = ping()
    json_body = [{"measurement": "internet", "fields": {"value": o}}]

    try:
        client.write_points(json_body)
    except:
        print("error: writing to database")

    s.enter(15, 1, ctrlp, (client,))

"""
get/write to database every 10 minuits 
"""
def ctrls(client):
    stathole = pihole()
    statspeed = speed()
    
    json_body = [{"measurement": "ping", "fields": {"value": float(statspeed["ping"])}},
                 {"measurement": "up", "fields": {"value": float(statspeed["up"])}},
                 {"measurement": "down", "fields": {"value": float(statspeed["down"])}},
                 {"measurement": "dns_queries", "fields": {"value": float(stathole["dns_queries_today"])}},
                 {"measurement": "ads_per", "fields": {"value": float(stathole["ads_percentage_today"])}},
                 {"measurement": "ads_blocked", "fields": {"value": float(stathole["ads_blocked_today"])}},
                 {"measurement": "pi_clients", "fields": {"value": float(stathole["unique_clients"])}},
                 {"measurement": "un_domains", "fields": {"value": float(stathole["unique_domains"])}},
                 {"measurement": "bl_domains", "fields": {"value": float(stathole["domains_being_blocked"])}},
                 {"measurement": "gravup", "fields": {"value": float(stathole["gravup"])}},
                ]
    try:
        client.write_points(json_body)
    except:
        print("error: writing to database")

    #600
    s.enter(600, 1, ctrls, (client,))

"""
setup db connection and timer
"""
if __name__ == "__main__":
    #setup
    client = InfluxDBClient(host='monpi.lan', port=8086)
    client.switch_database('net')
    s = sched.scheduler(time.time, time.sleep)

    #timers
    s.enter(15, 1, ctrlp, (client,))
    s.enter(600, 1, ctrls, (client,))

    s.run()
