# Abstraction for send and get data from application
from appInterface import ApplicationInterface
from flask import Flask, redirect, url_for, request
import atexit
from multiprocessing import Process
import threading
import psutil
import os 
import time

import pandas as pd
import datetime as dt
from datetime import timedelta, date

import numpy as np 
from keras.models import Sequential
from keras.layers import Dense, SimpleRNN
from keras.callbacks import EarlyStopping
from sklearn.metrics import mean_absolute_error, mean_squared_error

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import matplotlib as plt

# TO CONNECT TO API to get or post DATA
URL = "http://192.168.0.219:8000/"
URL = "http://192.168.56.1:8000/"
LOCAL_IP = "192.168.56.1" #socket.gethostbyname(socket.gethostname())#"192.168.0.219" #IP OF THNE APP
LOCAL_IP = "127.0.0.1"
APPNAME="demoEdgeNode"

interface = ApplicationInterface(URL)
app = Flask(__name__)

def startCommunication():
    server = Process(target=app.run(debug= True, port=5000))
    server.start()    

def stopCommunication(server):
    server.terminate()
    server.join()

def hiSignalToAPI():
    startCommunication()
    interface.postIP(LOCAL_IP,'12','appIP',APPNAME)# SEND THE IP OF THE APP TO THE API
    print('[+] IP send to the API', LOCAL_IP)

def byeSignalToAPI():
    stopCommunication(app)
    interface.deleteAppIPbyName(APPNAME)
    print('[+] IP remove from API')
    
# TEST FUNCTION
#=======================================================================
@app.route('/hi')
def query_example():
    return 'Hello there'
#=======================================================================

@app.route('/send-ip')
def send_ip():
    try:
        interface.postIP(LOCAL_IP,'12',APPNAME) # SEND THE IP OF THE APP TO THE API
        return LOCAL_IP
    except:
        return 'DEBUG: Error sending IP'
    
@app.route('/send-use')
def send_use():
    try:
        res = interface.postUse(LOCAL_IP, '12', APPNAME)
        cpu = res["data"]["values"][0]["value"]["CPU"]
        ram = res["data"]["values"][0]["value"]["RAM"]
        out = "CPU use:" + str(cpu) + "% | RAM use:" + str(ram) + "%" 
        return out
    except:
        return 'DEBUG: Error sending local machine use'
    
@app.route('/transmit',methods = ['POST'])
def transmit():
    if request.method == 'POST':
      print(request)

@app.route('/get',methods = ['GET'])
def get():
    print(request)
    return "test"

@app.route('/predict')
def run_app():
    try:
        # GET IP OF THE APP GIVEN THE NAME
        APPNAME="demoAppPred"
        appIP = interface.getAppIPbyName(APPNAME)['data']
        print("[+] Prediction AppIP:", appIP)
        
        # ASK THE APP PREDICTION TRAIN THE MODEL
        s = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        s.mount('http://', adapter)
        _appURL = "http://" + appIP + ":5000/run-app"
        resp = s.get(url=_appURL)
        print('[+] Status from pred app:',resp.text)
        res = resp.text
        
        
        # Example : Using the model trained by a remote app
        model = interface.getKerasModel(appIP) # Get the model from the server
        print(model.summary())
        print("[+] Trained model received from the app:", type(model))
        
        res = interface.getListOfMessageFromSensorType("deg")
        data = res['data']

        pred = makePrediction(model, data)

        print("[+] Prediction made by the Edge")
        res = str(pred)
    
    except:
        res = "Application does not seem to have worked properly :/"
    return res


def makePrediction(model, data):
    temp = []; dates = []; newdates = []; newtemp = []; df = pd.DataFrame(); newdf = pd.DataFrame()
    for dat in data:
        temp.append(dat['values'][0]['value'])
        dat = dt.datetime.fromtimestamp(dat['values'][0]['date']).strftime('%Y-%m-%d')
        dates.append(dat)
    df["date"]=dates; df["temp"]=temp
    df = df.drop_duplicates(subset=['date'])
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    starting = (today - timedelta(days=300))
    times = pd.date_range(str(starting).replace("-",""), str(d1).replace("-",""), freq="D")
    for _, row in df.iterrows():
        if(row["date"].replace("-","") in times):
            newdates.append(int(row["date"].replace("-","")))
            newtemp.append(row["temp"])
    newdf["date"]=newdates; newdf["temp"]=newtemp
    print("[+] Clean dataframe built")
    train_size = 150
    train, test = newdf.iloc[:train_size], newdf.iloc[train_size:]
    trainY, trainX = np.array(train["temp"].values.tolist()), np.array(train["date"].values.tolist())
    testY, testX = np.array(test["temp"].values.tolist()), np.array(test["date"].values.tolist())
    print("[+] Test and train set built")
    train_predict = model.predict(trainX)
    test_predict = model.predict(testX)
    print('Train Root Mean Squared Error(RMSE): %.2f; Train Mean Absolute Error(MAE) : %.2f '
        % (np.sqrt(mean_squared_error(trainY, train_predict[:,0])), mean_absolute_error(trainY, train_predict[:,0])))
    print('Test Root Mean Squared Error(RMSE): %.2f; Test Mean Absolute Error(MAE) : %.2f ' 
        % (np.sqrt(mean_squared_error(testY, test_predict[:,0])), mean_absolute_error(testY, test_predict[:,0])))
    return test_predict

def model_dnn():
    model=Sequential()
    model.add(Dense(units=32, input_dim=1, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error',  optimizer='adam',metrics = ['mse', 'mae'])
    return model

def main():
    hiSignalToAPI()

if __name__ == '__main__':
    main()
    byeSignalToAPI()

atexit.register(byeSignalToAPI)