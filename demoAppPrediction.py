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

import json
import pickle
from collections import OrderedDict

from keras.models import Sequential
from keras.layers import Dense, SimpleRNN
from keras.callbacks import EarlyStopping
import numpy as np 
from sklearn.metrics import mean_absolute_error, mean_squared_error

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
URL = "http://192.168.56.1:8000/ec/payloads"
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
    starting = (today - timedelta(days=300))
    times = pd.date_range(str(starting).replace("-",""), str(d1).replace("-",""), freq="D")
    
    newdf = pd.DataFrame()
    newdates = []; newtemp = []
    for index, row in df.iterrows():
        if(row["date"].replace("-","") in times):
            newdates.append(int(row["date"].replace("-","")))
            newtemp.append(row["temp"])
    newdf["date"]=newdates; newdf["temp"]=newtemp
        
    print("Dataset:", len(newdf))
    #Split data set into testing dataset and train dataset
    train_size = 150
    #train, test =newdf.values[0:train_size,:],newdf.values[train_size:len(newdf.values),:]
    train, test = newdf.iloc[:train_size], newdf.iloc[train_size:]
    # setup look_back window 

    #convert dataset into right shape in order to input into the DNN
    trainY, trainX = np.array(train["temp"].values.tolist()), np.array(train["date"].values.tolist())
    testY, testX = np.array(test["temp"].values.tolist()), np.array(test["date"].values.tolist())
        
    model = model_dnn()
    
    history=model.fit(trainX,trainY, epochs=100, batch_size=30, verbose=1, validation_data=(testX,testY),callbacks=[EarlyStopping(monitor='val_loss', patience=10)],shuffle=False)
    
    train_predict = model.predict(trainX)
    test_predict = model.predict(testX)
    print('Train Root Mean Squared Error(RMSE): %.2f; Train Mean Absolute Error(MAE) : %.2f '
        % (np.sqrt(mean_squared_error(trainY, train_predict[:,0])), mean_absolute_error(trainY, train_predict[:,0])))
    print('Test Root Mean Squared Error(RMSE): %.2f; Test Mean Absolute Error(MAE) : %.2f ' 
        % (np.sqrt(mean_squared_error(testY, test_predict[:,0])), mean_absolute_error(testY, test_predict[:,0])))

    sendTrainedModel(model)
    
    try:
        return test_predict
    except:
        return None


# EXAMPLE OF MODEL, THIS MODEL AND THE PREDICTION ARE VERY BAD - This for example purpose
def model_dnn():
    model=Sequential()
    model.add(Dense(units=32, input_dim=1, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error',  optimizer='adam',metrics = ['mse', 'mae'])
    return model



def sendTrainedModel(model):
    print("[+] Saving model")

    model_json = model.to_json()
    with open("fitted_model.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights("fitted_model.h5")

    dict = {'values': [{'id': "999999", 'date': 1000, 'parameterId': "999999", 'value': model_json}]}
    interface.postDataFromSingleDeviceDict("0.0.0.0", 1000, "model", dict)
    
    print("[+] Model sent")

if __name__ == '__main__':
    main()
    byeSignalToAPI()

atexit.register(byeSignalToAPI)