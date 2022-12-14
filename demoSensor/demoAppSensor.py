from appInterface import ApplicationInterface
from datetime import date, timedelta
from tqdm import tqdm
import numpy as np
import pandas as pd
import schedule
import socket
import statistics 
import random 

import matplotlib.pyplot as plt

# python3.9 demoAppSensor.py
# docker build -t demosensor .
# docker run demosensor

SERVERURL = "http://192.168.0.192:8000/" # Change here
EDGEURL = "http://127.0.0.1:5000/"

SENDING_DATA_TIME_INTER = 1 # in minutes
GETTING_DATA_TIME_INTER = 1 # in minutes
NUMBER_DATA_TO_SEND = 10
CONTAINER_IP = socket.gethostbyname(socket.gethostname())

interface = ApplicationInterface(SERVERURL)

def main():
    
    print("[+] Container IP : ", CONTAINER_IP)
    print("[+] Delete all old data for the experiment")
    interface.deleteAllData() # Change here
    print("[+] Sensor running ...")
    sendData(300)
    #schedule.every(SENDING_DATA_TIME_INTER).minutes.do(lambda: sendData(NUMBER_DATA_TO_SEND))
    #schedule.every(GETTING_DATA_TIME_INTER).minutes.do(lambda: getData())
    '''
    sendData(NUMBER_DATA_TO_SEND)
    getData()
    '''
    """
    while True:
        schedule.run_pending()            
    """
    
    """
    lst_send_mean = []
    lst_get_mean = []
    lst_i = []
    for i in range(0, 100):
        send_mean, send_std = sendData(NUMBER_DATA_TO_SEND)
        get_mean, get_std = getData() 
        lst_send_mean.append(send_mean)
        lst_get_mean.append(get_mean)
        lst_i.append(i)
    plotResponseTime(lst_x=lst_send_mean, lst_x2=lst_get_mean, lst_y=lst_i, title="Experiment - Post/Get")
    """

def plotResponseTime(lst_x, lst_x2, lst_y, title):
        fig = plt.figure(figsize = (12, 5))
        plt.plot(lst_y, lst_x, color ='cornflowerblue', label="Post - Average value")
        plt.plot(lst_y, lst_x2, color ='green', label="Get - Average value")
        
        plt.ylabel("Average value")
        plt.xlabel("Request")
        plt.title(title)
        plt.xticks(rotation = 45, fontsize=8)
        plt.legend()
        plt.subplots_adjust(bottom=0.2)
        name = title.replace("/","_") + ".png"
        try:
            plt.savefig(name)
        except:
            print("[-] Error - Unable to save the chart")

def getData():
    print("[+] Getting data")
    res = interface.getListOfMessageFromSensorType("test3") # Change here
    if(res==None):
        print("[!] Server is probably offline")
        datadict = None
    else:
        datadict = res['data']
        data = []
        for elem in datadict:
            data.append(elem['values'][0]['value'])
        return statistics.mean(data),statistics.stdev(data)

# Change here
def sendData(nbdata):
    print("[+] Sending data")
    mu, sigma = 0, 15 # mean and standard deviation for the normal distribution
    data = np.random.normal(mu, sigma, nbdata)
    y_data = getYData(data)
    pbar = tqdm(total=len(data))
    for i in range(0,len(data)):
        dict = {'values': [{'id': str(i), 'date': y_data[i], 'parameterId': str(i), 'value': data[i]}]}
        res = interface.postDataFromSingleDeviceDict(str(CONTAINER_IP), y_data[i], "test3", dict)
        if(res==None):
            print("[!] Server is probably offline")
            break
        pbar.update(1)
    pbar.close()
    return statistics.mean(data),statistics.stdev(data) 

# Change here
def getYData(data):
    y_data = []
    for i in range(0, len(data)):
        if(data[i]>=0):
            y_data.append(1)
        else:
            y_data.append(-1)
    return y_data

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