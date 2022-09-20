import argparse
from datetime import datetime, date, timedelta
import numpy as np
from tqdm import tqdm
import pandas as pd

from appInterface import ApplicationInterface

URL = "http://192.168.0.219:8000/"
URL = "http://192.168.56.1:8000/"
interface = ApplicationInterface(URL)

def main(args):
    sendData(args.n)
    
def sendData(nbdata):
    mu, sigma = 15, 5 # mean and standard deviation for the normal distribution
    data = np.random.normal(mu, sigma, nbdata)
    dates = getRandomDate(len(data))
    pbar = tqdm(total=len(data))
    for i in range(0,len(data)):
        dict = {'values': [{'id': str(i), 'date': dates[i], 'parameterId': str(i), 'value': data[i]}]}
        interface.postDataFromSingleDeviceDict("192.168.56.1", dates[i], "deg", dict)
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
    parser = argparse.ArgumentParser(description="Process args for edge computing project")
    parser.add_argument("--v", help="Verbose (0/1)", type=int, default=0)
    parser.add_argument("--min", help="Send data every x minutes (int)", type=int, default=5)
    parser.add_argument("--n", help="Number of data to send at each iteration (int)", type=int, default=500)
    args = parser.parse_args()
    main(args)