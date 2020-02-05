import socket
import sys
import sched, time
import random
from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%d/%m/%y,%H:%M:%S")
s = sched.scheduler(time.time, time.sleep)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# server_address = ('18.221.174.251', 8080)
server_address = ('192.168.1.4', 9090)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

def do_something(sc):
    print("Doing stuff...")

    s.enter(100, 1, do_something, (sc,))

    try:
        # gps data
        ratitude = random.randrange(100, 600, 3);
        message = '!D,'+dt_string+',51.405'+ str(ratitude) +',0.541'+ str(ratitude) +',1,344,130000,11.9,100,4,6,0;'
        if sys.version_info < (3, 0):
            data = bytes(message)
        else:
            data = bytes(message, 'utf8')

        print(str(message))
        sock.sendall(data)

        # Look for the response from tcp server
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            recvData = sock.recv(16)
            amount_received += len(recvData)
            print(str(recvData))

    finally:
        print('closing socket')
        # sock.close()

s.enter(100, 1, do_something, (s,))
s.run()

