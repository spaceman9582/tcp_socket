import socket
import datetime
import re
import pymongo
from time import mktime
from multiprocessing import Process

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
db = myclient['new_miitrace_db']

def convertRecvData(str):

    return

def turnOnDevice_status(iemi):
    print("arrived in turnOnDevice_status")
    devicesCollection = db['devices']
    imei_db = devicesCollection.find({"iemi": iemi}, {"device_status": 1})
    for x in imei_db:
        newValues = { "$set": { "device_status": "1" }}
        status = devicesCollection.update_one({"iemi": iemi}, newValues)
        print("device_status update :" + status)
    # if imei_db:
    #     print("turn on device, Iemi:"+ iemi)
    #     imei_db['device_status'] = 1;
    #     status = devicesCollection.update_one({"iemi": iemi}, imei_db)
    #     print(status)

def saveImeiListToDb(imei, ip_address_port):
    print("arrived in saveImeiListToDb")
    imeiCollection = db['imei_ip_address_lists']
    insert_data = {
                "imei": imei,
                "ip_address": ip_address_port
            }

    x = imeiCollection.insert_one(insert_data)
    print("save imei status::", x)
    return;

def checkImeiRegisteredStatusInDb(imei, ip_address_port):
    print("arrived in checkImeiRegisteredStatusInDb")
    imeiCollection = db["imei_ip_address_lists"]
    imei_ip_address_data = imeiCollection.find({"imei": imei, "ip_address": ip_address_port}, {"imei": 1, "ip_address":1})
    count = 0
    for x in imei_ip_address_data:
        count += 1
    array_num = count
    print("imei is :", array_num)
    if array_num > 1:
        return True
    else:
        return False

def getImeiFromIpAddressInDb(ip_add):
    print("arrived in getImeiFromIpAddressInDb, ip_add"+ip_add)
    imeiCollection = db["imei_ip_address_lists"]
    imei_db = imeiCollection.find_one({"ip_address": ip_add},{"imei":1, "ip_address": 1})
    imei = imei_db['imei']
    print("imei_db:", imei)
    return imei

def saveGpsDataToDB(device_data, ip_address_port):
    print("arrived in saveGpsDataToDB, ip_address" + ip_address_port)
    result = [x.strip() for x in device_data.split(',')]
    insert_data = {}
    if result[0] == '!1':
        imei_data = result[1]
        imei = re.sub(';', '', imei_data)
        print("imei:::" + imei)
        turnOnDevice_status(imei)
        # if imei is registered in db
        # Yes:=>system start
        # No: =>register "imei & ip address & port" in db

        checkImeiRegisteredStatusInDb_flag = checkImeiRegisteredStatusInDb(imei, ip_address_port)
        if not checkImeiRegisteredStatusInDb_flag:
            saveImeiListToDb(imei, ip_address_port)

    elif result[0] == '!D':
        # get imei from ip address in db
        imei = getImeiFromIpAddressInDb(ip_address_port)
        print("arrived in !D, imei:"+imei)

        turnOnDevice_status(imei)
        eventcode = '{:024b}'.format(int(result[7], 16))
        nowTime = datetime.datetime.now()
        device_date = result[1]+" "+result[2]
        datetime_obj = datetime.datetime.strptime(device_date, '%d/%m/%y %H:%M:%S')
        print("datetime_obj:",datetime_obj)
        timeStamp = mktime(datetime_obj.timetuple())
        print("timeStamp", timeStamp)
        insert_data = {
            "imei": imei,
            "date": result[1],
            "time": result[2],
            "latitude": result[3],
            "longitude": result[4],
            "speed": result[5],
            "direction": result[6],
            "locating": eventcode[22:24],
            "working": eventcode[20:22],
            "SOS": eventcode[17:18],
            "overspeed": eventcode[16:17],
            "fall": eventcode[15:16],
            "geofence1": eventcode[14:15],
            "geofence2": eventcode[13:14],
            "geofence3": eventcode[12:13],
            "battery_alarm": eventcode[11:12],
            "motion": eventcode[9:10],
            "movement": eventcode[8:9],
            "signal_strength": eventcode[3:8],
            "switch_on": eventcode[2:3],
            "charging": eventcode[1:2],
            "altitude": result[8],
            "battery_level": result[9],
            "sattelites_in_use": result[10],
            "sattelites_available": result[11],
            "Reserved": result[12],
            "created_on": nowTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "created_milli": timeStamp *1000
        }
        manageDatabase(insert_data)
    # elif result[0] == '!3':
    #     insert_data = {
    #         "data_info":str,
    #         "Protocol": result[0],
    #         "response": result[1]
    #     }
    # elif result[0] == '!4':
    #     insert_data = {
    #         "data_info":str,
    #         "Protocol": result[0],
    #         "responseFunction": result[1]
    #     }
    # elif result[0] == '!7':
    #     insert_data = {
    #         "data_info":str,
    #         "Protocol": result[0],
    #         "firmwre_version": result[1],
    #         "signal_strength": result[2]
    #     }
    # elif result[0] == '!5':
    #     insert_data = {
    #         "data_info":str,
    #         "Protocol": result[0],
    #         "CSQ":result[1],
    #         "GPS_location": result[2]
    #     }

    return;


def printme(str):
    print(str)
    return ;


def manageDatabase(insert_data):

    collection = db['device_datas']
    x = collection.insert_one(insert_data)
    return;


def printLogfile(str):
    with open("log.txt", "a+") as text_file:
        text_file.write("%s\r\n" % str)


def start(connection, client_address):

    print('connection from', client_address[0])
    # print('client port is ', client_port)
    i = 0
    # Receive the data in small chunks and retransmit it
    while True:
        recvDataFromClient = connection.recv(4096)
        # data = json.loads(response_data.decode("utf-8"))
        # data = json.loads(resp_parsed)

        if recvDataFromClient:
            connection.sendall(recvDataFromClient)
            recvDataString = recvDataFromClient.decode("utf-8")

            printLogfile(recvDataString)

            print(recvDataString)

            cli_add = client_address[0];
            cli_port = client_address[1];
            ip_address_port = cli_add + ":" + str(cli_port)
            # recvDataString = str(recvDataFromClient, 'utf-8')
            saveGpsDataToDB(recvDataString, ip_address_port)

        else:
            # print('no data from', client_address)
            break


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 9090)
print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
# Listen for incoming gps device connections
sock.listen(5)

while True:
    # Wait for a gps device connection
    print('waiting for a Gps Device connection')
    connection, client_address = sock.accept()
    cli_address, client_port = sock.getsockname()
    subs = Process(target=start, args=(connection, client_address, ))
    subs.start()
    connection.close()


