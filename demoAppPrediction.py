# Abstraction for send and get data from application
from appInterface import ApplicationInterface
from flask import Flask
import atexit
from multiprocessing import Process

import pandas as pd
import datetime as dt
from datetime import timedelta, date

# For prediction task
import numpy as np 
from keras.models import Sequential
from keras.layers import Dense, SimpleRNN
from keras.callbacks import EarlyStopping
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
URL = "http://192.168.0.219:8000/"
URL = "http://192.168.0.192:8000/"
LOCAL_IP = "127.0.0.2" #socket.gethostbyname(socket.gethostname())#"192.168.0.219" #IP OF THNE APP
APPNAME="demoAppPredNew"

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
    interface.postIP(LOCAL_IP,'12',APPNAME)# SEND THE IP OF THE APP TO THE API
    print('[+] IP send to the API', LOCAL_IP)

def byeSignalToAPI():
    stopCommunication(app)
    interface.deleteAppIPbyName(APPNAME)
    print('[+] IP remove from API')
    
# TEST FUNCTION
#=======================================================================
@app.route('/')
def home():
    return 'App for the training of the model is online !'


@app.route('/hi')
def query_example():
    hiSignalToAPI()
    return 'Hello there'

@app.route('/delete-all')
def delete_all():
    res = interface.deleteAllData()
    return res

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
        
# Change here
@app.route('/run-app')
def run_app():
    #try:
    # YOUR CODE HERE
    print("[+] Getting data")
    res = interface.getListOfMessageFromSensorType("test3")
    data = res['data']
    res = str(trainModel(data))
    """
    except:
        res = "Application does not seem to have worked properly :/"
    """
    return res

def main():
    hiSignalToAPI()


# Change here
def trainModel(data):
    temp = []; dates = [];
    newdf = pd.DataFrame()
    for dat in data:
        temp.append(dat['values'][0]['value'])
        dates.append(dat['values'][0]['date'])
    newdf["date"]=dates; newdf["temp"]=temp
        
    train_size = 200 # As the sensor send 300 data in our example the test size is 100
    train, test = newdf.iloc[:train_size], newdf.iloc[train_size:]
    trainX, trainY = np.array(train["temp"].values.tolist()), np.array(train["date"].values.tolist())
    testX, testY = np.array(test["temp"].values.tolist()), np.array(test["date"].values.tolist())
    model = model_dnn()
    print(trainX)
    history=model.fit(trainX,trainY, epochs=10, batch_size=2, verbose=1, validation_data=(testX,testY),shuffle=True)
        
    """
    train_predict = model.predict(trainX)
    test_predict = model.predict(testX)
    print('Train Root Mean Squared Error(RMSE): %.2f; Train Mean Absolute Error(MAE) : %.2f '
        % (np.sqrt(mean_squared_error(trainY, train_predict[:,0])), mean_absolute_error(trainY, train_predict[:,0])))
    print('Test Root Mean Squared Error(RMSniceoclockbe@niceoclockbeE): %.2f; Test Mean Absolute Error(MAE) : %.2f ' 
        % (np.sqrt(mean_squared_error(testY, test_predict[:,0])), mean_absolute_error(testY, test_predict[:,0])))
    """
    
    print("[+] Sending new model")
    try:
        interface.postKerasModel(model, LOCAL_IP, "100", APPNAME)
        print("[+] Trained model sent")
        return "New model sent"
    except:
        return "Error :("

# Change here
def model_dnn():
    model=Sequential()
    model.add(Dense(units=4, input_dim=1, activation='relu'))
    model.add(Dense(4, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer="adam",
              loss='categorical_crossentropy',
              metrics=['accuracy'])
    return model

if __name__ == '__main__':
    app.run(host='127.0.0.2', port=5000)
    main()
    byeSignalToAPI()

atexit.register(byeSignalToAPI)