import psutil, os 

def get_mem():
    mem = list(os.popen('free -t -m').readlines()[-1].split()[2:])
    mem = [i[:-1] for i in mem]
    print(mem)
    return mem

def pi_temp():
    rtemp = os.popen('vcgencmd measure_temp').readlines()[0].strip().replace("temp=","")[:-2]
    print(rtemp)
    return rtemp

if __name__ == "__main__":

    hostname = os.popen('hostname').readlines()[0].strip()
    
    if hostname 
