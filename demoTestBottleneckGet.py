from appInterface import ApplicationInterface
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import matplotlib.pyplot as plt
import time
import pandas as pd
import os
import psutil

def main():
    API_URL = "http://192.168.0.219:8000/"
    interface = ApplicationInterface(API_URL)

    # GET IP OF THE APP GIVEN THE NAME
    APPNAME="testAppPrediction"
    appIP = interface.getAppIPbyName(APPNAME)['data']
    
    appIP = "127.0.0.1"
    
    print("[+] AppIP:", appIP)

    # CALL THE APP
    s = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('http://', adapter)
    _appURL = "http://" + appIP + ":5000/run-app"

    lst_x = []; lst_y = []; lst_CPU = []
    NB_REQUEST = 100
    for i in range(0, NB_REQUEST): 
        
        st = time.time()
        resp = s.get(url=_appURL)
        ed = time.time()
        
        l1, l2, l3 = psutil.getloadavg()
        CPU = (l3/os.cpu_count()) * 100
        
        tim = (ed-st)
    
        lst_y.append(tim)
        lst_x.append(i)
        lst_CPU.append(CPU)
        #print('[+] Message from App:',resp.text)

    plotResponseTime(NB_REQUEST, lst_x, lst_y, "App prediction - Average request time")
    #plotResponseTime(NB_REQUEST, lst_x, lst_CPU, "App prediction - Average CPU time")


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
    main()