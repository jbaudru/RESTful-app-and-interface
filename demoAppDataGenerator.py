import argparse
import time
from datetime import datetime
import calendar
import numpy as np
import schedule
from tqdm import tqdm
import pandas as pd
import random

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
    schedule.every(args.min).minutes.do(sendData, args.n)
    while True:
        schedule.run_pending()
        time.sleep(1)

def sendData(nbdata):
    mu, sigma = 15, 5 # mean and standard deviation for the normal distribution
    data = np.random.normal(mu, sigma, nbdata)
    dates = getRandomDate(len(data))
    pbar = tqdm(total=len(data))
    for i in range(0,len(data)):
        dict = {'values': [{'id': str(i), 'date': dates[i], 'parameterId': str(i), 'value': data[i]}]}
        interface.postDataFromSingleDeviceDict("192.168.56.1", dates[i], "testLocalNet", dict)
        pbar.update(1)
    pbar.close()

def getRandomDate(lenght):
    dates = []
    tmpdates = pd.date_range('2000-01-01', '2022-01-01', freq='D')
    tmpdates = tmpdates[:lenght]
    for date in tmpdates:
        dates.append(int(round(date.timestamp())))
        #dates.append(int(str(date).split(" ")[0].replace("-","")))
    return dates

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process args for edge computing project")
    parser.add_argument("--v", help="Verbose (0/1)", type=int, default=0)
    parser.add_argument("--min", help="Send data every x minutes (int)", type=int, default=5)
    parser.add_argument("--n", help="Number of data to send at each iteration (int)", type=int, default=10)
    args = parser.parse_args()
    main(args)
