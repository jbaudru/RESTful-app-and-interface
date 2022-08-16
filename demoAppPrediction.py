# Abstraction for send and get data from application
from code import interact
from appInterface import ApplicationInterface

# For prediction task
import pandas as pd
import random
import datetime as dt
from darts import TimeSeries
from darts.models import ExponentialSmoothing

# For the application to be called by the API or others nodes
from flask import Flask
from multiprocessing import Process
import socket
import atexit
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

# TO LISTEN FROM CALL FROM API
app = Flask(__name__)

def startCommunication(app):
    #server = Process(target=app.run(host=LOCAL_IP, debug= True, port=5000))
    server = Process(target=app.run(debug= True, port=5000))
    server.start()    

def stopCommunication(server):
    server.terminate()
    server.join()

@app.route('/hi')
def query_example():
    return 'Hello there'

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
    try:
        interface.postIP(LOCAL_IP,'12','appIP',APPNAME)# SEND THE IP OF THE APP TO THE API
        print('[+] IP send to the API', LOCAL_IP)
    except:
        print('DEBUG: Error sending IP')
    startCommunication(app)


def exit_handler():
    stopCommunication(app)
    interface.deleteAppIPbyName(APPNAME)
    print('[+] IP remove from API')


# Just a random function to demonstrate the principle
# YOUR CODE HERE
def makePrediction(data):
    print("[+] Making predictions")
    temp = []; date = []; df = pd.DataFrame()
    for dat in data:
        temp.append(dat['values'][0]['value'])
        dat = dt.datetime.fromtimestamp(dat['values'][0]['date']).strftime('%Y-%m-%d')
        date.append(dat)
    df["date"]=date; df["temp"]=temp
    df = df.drop_duplicates(subset=['date'])
    size_pred = 7 # Number of day

    end = str(dt.date(2000,4,9) + dt.timedelta(days=14)).replace("-","")
    times = pd.date_range('20000101', end, freq="D")

    series = TimeSeries.from_dataframe(df, 'date', 'temp', fill_missing_dates=True, freq=None)
    train, val = series[:-size_pred], series[-size_pred:]

    model = ExponentialSmoothing()

    print("[+] Fitting model for timeseries prediction")
    model.fit(train)
    prediction = model.predict(len(val), num_samples=len(times))

    ind = random.randint(0,len(prediction.values()-1))
    try:
        return prediction.values()[ind][0]
    except:
        return 666

if __name__ == '__main__':
    main()
