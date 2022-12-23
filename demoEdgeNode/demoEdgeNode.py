# Abstraction for send and get data from application
from appInterface import ApplicationInterface
from flask import Flask, redirect, url_for, request, current_app
import atexit
from multiprocessing import Process

import pandas as pd
import datetime as dt
from datetime import timedelta, date

import numpy as np 

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import matplotlib as plt

"""
docker build -t app_demo_edge .
docker run -p 5000:5000 -d app_demo_edge
"""

# TO CONNECT TO API to get or post DATA
URL = "http://192.168.0.192:8000/" # Change here
LOCAL_IP = "192.168.56.1" #socket.gethostbyname(socket.gethostname())#"192.168.0.219" #IP OF THNE APP
LOCAL_IP = "127.0.0.1"
APPNAME="demoEdgeNode"

interface = ApplicationInterface(URL)
app = Flask(__name__)

def startCommunication():
    server = Process(target=app.run(debug= True, port=6000))
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
@app.route('/')
def home():
    return 'App for the  testing of the model is online !'

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

# Change here
@app.route('/fetch-model')
def index():
    # GET IP OF THE APP GIVEN THE NAME
    APPNAME="demoAppPredNew"
    try:
        appIP = interface.getAppIPbyName(APPNAME)['data']
        print("[+] Prediction AppIP:", appIP)
    except:
        print("[+] Application '", APPNAME, "' not found.")
        return "No application named " + APPNAME + " in the database."
    try:
        # Example : Using the model trained by a remote app
        model = interface.getKerasModel(appIP) # Get the model from the server
        print(model.summary())
        print("[+] Trained model received from the app:", type(model))
            
        res = interface.getListOfMessageFromSensorType("test3")
        data = res['data']
        
        current_app.model = model
        current_app.data = data
        return 'Objects stored in application context'
    except:
        return "No model found"


# Change here
@app.route('/predict')
def run_app():
    try:
        print("[+] Prediction made by the Edge")
        pred = makePrediction(current_app.model, current_app.data)
        res = pred
    except:
        if(current_app.model==None):
            res = "You should fetch the model first!"
        else:
            res = "Application does not seem to have worked properly :/"
    return res

# Change here
def makePrediction(model, data): #data can be remplace by any value
    output =""
    testX= np.array([12.4]) #temperature
    trueY= np.array([1])
    print("Temp X:",testX)
    print("True Y:", trueY)
    predY = model.predict(testX, verbose=0)
    print("Predicted Y:", predY)
    
    output += "Temp X:" + str(testX) + "<br>"
    output += "True Y:" + str(trueY) + "<br>"
    if(predY>0):
        resY = 1
    else:
        resY = -1
    output += "Pred Y:" + str(resY)
    return output


def main():
    hiSignalToAPI()

if __name__ == '__main__':
    main()
    byeSignalToAPI()

atexit.register(byeSignalToAPI)