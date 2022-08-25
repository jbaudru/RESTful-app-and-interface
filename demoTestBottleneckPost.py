import argparse
import time
from datetime import datetime, date, timedelta
import calendar
import numpy as np
import schedule
from tqdm import tqdm
import pandas as pd
import random
import matplotlib.pyplot as plt
import os

from appInterface import ApplicationInterface

"""
========================================================
Note:
------
The purpose of this application is to show how
to use the python interface to interact with the API.

The goal of this application is to generate data
according to a certain distribution and to send
them at regular intervals to a network node.

Command:
--------
python .\demoAppDataGenerator.py --min 1 --n 5

https://github.com/jbaudru & https://github.com/llucbono
========================================================
"""

URL = "http://192.168.0.219:8000/ec/payloads"
interface = ApplicationInterface(URL)

def main(args):
    sendData(args.n)

def sendData(nbdata):
    lst_x = []; lst_y = [];
    step = [i for i in range(10, 500, 10)]
    for stp in step:
        mu, sigma = 15, 5 # mean and standard deviation for the normal distribution
        data = np.random.normal(mu, sigma, stp)
        dates = getRandomDate(len(data))
        tottime = 0
        pbar = tqdm(total=len(data))
        for i in range(0,len(data)):
            dict = {'values': [{'id': str(i), 'date': dates[i], 'parameterId': str(i), 'value': data[i]}]}
            st = time.time()
            interface.postDataFromSingleDeviceDict("192.168.56.1", dates[i], "deg", dict)
            ed = time.time()
            tottime += (ed-st)
            pbar.update(1)
        lst_y.append(tottime)
        lst_x.append(stp)

    plotResponseTime(len(data), lst_x, lst_y, "App POST - Average request time")
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

def plotResponseTime(NB_REQUEST, lst_x, lst_y, title):
        data = pd.DataFrame(lst_y)
        t_average = data.rolling(NB_REQUEST//20).mean()
        fig = plt.figure(figsize = (12, 5))
        plt.plot(lst_x, lst_y, color ='cornflowerblue', label="Response time")
        plt.plot(lst_x, t_average, color ='red', label="Average")
        plt.ylabel("Time (s)")
        plt.xlabel("Request")
        plt.title(title)
        plt.xticks(rotation = 45, fontsize=8)
        plt.legend()
        plt.subplots_adjust(bottom=0.2)
        name = os.getcwd() + title + ".png"
        try:
            plt.savefig(name)
        except:
            print("[-] Error - Unable to save the chart")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process args for edge computing project")
    parser.add_argument("--v", help="Verbose (0/1)", type=int, default=0)
    parser.add_argument("--min", help="Send data every x minutes (int)", type=int, default=5)
    parser.add_argument("--n", help="Number of data to send at each iteration (int)", type=int, default=100)
    args = parser.parse_args()
    main(args)
