from fritzconnection import FritzConnection
from fritzconnection import fritzstatus


fc = FritzConnection(address='192.168.178.1', password='forts5980')

fw = FritzWLAN(fc)
print(fw.total_host_number)