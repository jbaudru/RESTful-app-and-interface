# Abstraction for send and get data from application
from appInterface import ApplicationInterface
from flask import Flask
import threading
import atexit
from multiprocessing import Process

# For prediction task
import pandas as pd
import random
import datetime as dt
from datetime import timedelta, date

import pickle
from darts import TimeSeries
from darts.models import ExponentialSmoothing
from darts.models import RNNModel


"""
========================================================
Note:
------
The purpose of this application is to show how
to use the python interface to interact with the API.

The goal of this application is to take data from
a node, make calculations (here prediction on future
data) and send the results back to a node.

Command:
--------
cd demo
docker build -t app_demo_prediction .
docker run -p 5000:5000 -d app_demo_prediction
docker run -p 5000:5000 --network host -d app_demo_prediction

requests.get('http://192.168.0.219:5000/hi').text
requests.get('http://192.168.0.219:5000/run-app').content

https://github.com/jbaudru & https://github.com/llucbono
========================================================
"""
# TO CONNECT TO API to get or post DATA
URL = "http://192.168.0.219:8000/ec/payloads"
LOCAL_IP = "192.168.0.219" #socket.gethostbyname(socket.gethostname())#"192.168.0.219" #IP OF THNE APP
APPNAME="demoAppPrediction"

interface = ApplicationInterface(URL)
app = Flask(__name__)

def startCommunication():
    server = Process(target=app.run(debug= True, port=5000))
    server.start()    

def stopCommunication(server):
    server.terminate()
    server.join()

def hiSignalToAPI():
    try:
        interface.postIP(LOCAL_IP,'12','appIP',APPNAME)# SEND THE IP OF THE APP TO THE API
        print('[+] IP send to the API', LOCAL_IP)
    except:
        print('DEBUG: Error sending IP to API')

def byeSignalToAPI():
    stopCommunication(app)
    interface.deleteAppIPbyName(APPNAME)
    print('[+] IP remove from API')

@app.route('/hi')
def query_example():
    return 'Hello there'

@app.route('/delete-all')
def delete_all():
    res = interface.deleteAllData()
    return res


@app.route('/send-ip')
def send_ip():
    try:
        interface.postIP(LOCAL_IP,'12','appIP',APPNAME) # SEND THE IP OF THE APP TO THE API
        return LOCAL_IP
    except:
        return 'DEBUG: Error sending IP'
        
@app.route('/run-app')
def run_app():
    try:
        # YOUR CODE HERE
        print("[+] Getting data")
        res = interface.getListOfMessageFromSensorType("deg")
        data = res['data']
        res = str(makePrediction(data))
    except:
        res = "Application does not seem to have worked properly :/"
    return res

def main():
    thread = threading.Thread(target=hiSignalToAPI)
    thread.start()
    startCommunication()

# Just a random function to demonstrate the principle
# YOUR CODE HERE
def makePrediction(data):
    print("[+] Making predictions based on the data stored in the API")
    temp = []; dates = []; df = pd.DataFrame()
    for dat in data:
        temp.append(dat['values'][0]['value'])
        dat = dt.datetime.fromtimestamp(dat['values'][0]['date']).strftime('%Y-%m-%d')
        dates.append(dat)

    df["date"]=dates; df["temp"]=temp
    df = df.drop_duplicates(subset=['date'])
        
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    lastweek = (today - timedelta(days=50))
    times = pd.date_range(str(lastweek).replace("-",""), str(d1).replace("-",""), freq="D")
    
    newdf = pd.DataFrame()
    newdates = []; newtemp = []
    for index, row in df.iterrows():
        if(row["date"].replace("-","") in times):
            newdates.append(row["date"])
            newtemp.append(row["temp"])
    newdf["date"]=newdates; newdf["temp"]=newtemp
    
    size_pred = 7 # Number of day    
    print("Times size:", len(times))
    
    series = TimeSeries.from_dataframe(newdf, 'date', 'temp', fill_missing_dates=True, freq=None)
    train, val = series[:-size_pred], series[-size_pred:]

    print("Train set size:",len(train))
    print("Test set size:", len(val))

    model = ExponentialSmoothing()
    #model = RNNModel(input_chunk_length=4)

    print("[+] Fitting model for timeseries prediction")
    model.fit(train) # PROB
    
    print("[+] Saving model")
    model.save("fitted_model.pt")
    sendTrainedModel(model)
    prediction = model.predict(len(val), num_samples=len(times))
    
    try:
        return prediction.values()
    except:
        return None

def sendTrainedModel(model):
    dict = {'values': [{'id': "999999", 'date': 1000, 'parameterId': "999999", 'value': model}]}
    interface.postDataFromSingleDeviceDict("192.168.56.1", 1000, "model", dict)
    print("[+] Model sent")

if __name__ == '__main__':
    main()
    byeSignalToAPI()

atexit.register(byeSignalToAPI)