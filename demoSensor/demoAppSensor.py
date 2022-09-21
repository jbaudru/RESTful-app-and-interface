from datetime import date, timedelta
import numpy as np
from tqdm import tqdm
import pandas as pd
import time 

import subprocess
import schedule
import socket

from appInterface import ApplicationInterface

# docker build -t demosensor .
# docker run demosensor

SERVERURL = "http://192.168.56.1:8000/"
SENDING_DATA_TIME_INTER = 1 # in minutes
GETTING_DATA_TIME_INTER = 1 # in minutes
NUMBER_DATA_TO_SEND = 500
CONTAINER_IP = socket.gethostbyname(socket.gethostname())

interface = ApplicationInterface(SERVERURL)

def main():
    
    print("[+] Container IP : ", CONTAINER_IP)
    
    print("[+] Sensor running ...")
    schedule.every(SENDING_DATA_TIME_INTER).minutes.do(lambda: sendData(NUMBER_DATA_TO_SEND))
    schedule.every(GETTING_DATA_TIME_INTER).minutes.do(lambda: getData())
    
    sendData(NUMBER_DATA_TO_SEND)
    getData()
    while True:
        schedule.run_pending()            

def getData():
    print("[+] Getting data")
    res = interface.getListOfMessageFromSensorType("deg")
    if(res==None):
        print("[!] Server is probably offline")
        data = None
    else:
        data = res['data']

def sendData(nbdata):
    print("[+] Sending data")
    mu, sigma = 15, 5 # mean and standard deviation for the normal distribution
    data = np.random.normal(mu, sigma, nbdata)
    dates = getRandomDate(len(data))
    pbar = tqdm(total=len(data))
    for i in range(0,len(data)):
        dict = {'values': [{'id': str(i), 'date': dates[i], 'parameterId': str(i), 'value': data[i]}]}
        res = interface.postDataFromSingleDeviceDict(str(CONTAINER_IP), dates[i], "deg", dict)
        if(res==None):
            print("[!] Server is probably offline")
            break
        pbar.update(1)
    pbar.close()

def getRandomDate(lenght):
    dates = []
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    lastweek = (today - timedelta(days=lenght))
    tmpdates = pd.date_range(lastweek, d1, freq='D')
    tmpdates = tmpdates[:lenght]
    for dat in tmpdates:
        dates.append(int(round(dat.timestamp())))
    return dates

if __name__ == '__main__':
    main()