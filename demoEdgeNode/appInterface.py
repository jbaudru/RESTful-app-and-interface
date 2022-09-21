"""
This class must be used to communicate with the RESTful API.
Some functions are restricted to the initial/final communication 
protocol between an application and the API and others to 
data exchange between an application and the API.

Note: To generate this doc use the command: pycco appInterface.py -p
 
"""
import requests
from requests.structures import CaseInsensitiveDict
import json
import numpy as np
import h5_to_json as h5j
import psutil
import keras

class ApplicationInterface:        
    def __init__(self, url):
        self.URL = url
        self.headers = CaseInsensitiveDict()
        self.headers["Content-Type"] = "application/json"
    
    
    # DATA EXCHANGE FUNCTIONS
    #---------------------------------------------------
    #---------------------------------------------------
    
    def getDataFromID(self, ID):
        """Returns the data of a node based on its ID

        Args:
            ID (str): ID of the node

        Returns:
            json: data of the node
        """
        url= self.URL + "ec/payloads/" + str(ID)
        return self.get(url)

    #---------------------------------------------------
    def getListOfMessageFromDeviceIP(self, IP):
        """Returns the data of a node based on its IP

        Args:
            IP (str): IP of the node

        Returns:
            json: data of the node
        """
        url= self.URL + "ec/payloads/sensor/?ip=" + str(IP)
        return self.get(url)
    
    #---------------------------------------------------
    def getListOfMessageByDate(self, date):
        """Returns the data of nodes based on their date

        Args:
            date (int): timestamp of the date

        Returns:
            json: data of the nodes
        """
        url= self.URL + "ec/payloads/offload/?date=" + str(date)
        return self.get(url)
    
    #---------------------------------------------------
    def getListOfMessageFromSensorType(self, typ):
        """Returns the data of nodes based on their type

        Args:
            typ (str): type of the nodes

        Returns:
            json: data of the nodes
        """
        url= self.URL + "ec/payloads/sensor_type/?type=" + str(typ)
        return self.get(url)

    #---------------------------------------------------
    def getListOfMessageWithValidation(self, val):
        """Returns the data of nodes based on their validation field

        Args:
            val (Boolean): value of data's validation field

        Returns:
            json: data of the nodes
        """
        url= self.URL + "ec/payloads/valid_items/?valid=" + str(val)
        return self.get(url)
    
    #---------------------------------------------------
    def deleteDataFromID(self, ID):
        """Removes data based on their ID

        Args:
            ID (str): ID of the node

        Returns:
            json: data of the node
        """
        url= self.URL + "ec/payloads/" + str(ID)
        return self.delete(url)
    
    #---------------------------------------------------
    def deleteAllData(self):
        """Delete all the data in the database

        Returns:
            json: data of the node
        """
        url= self.URL + "ec/payloads/all/"
        return self.delete(url)
    
    #---------------------------------------------------
    def deleteListOfMessageByDate(self, date):   
        """Removes data based on their date

        Args:
            date (int): timestamp date of the data

        Returns:
            json: data of the node
        """ 
        url= self.URL + "ec/payloads/offload/?date=" + str(date)
        return self.delete(url)
    
    #---------------------------------------------------
    def postDataFromSingleDevice(self, ip: str, date: int, type: str, jsonfile: str):
        """Add data from a single device to the database of a node

        Args:
            ip (str): IP of the sender device
            date (int): timestamp of the data
            type (str): type of the data
            jsonfile (str): path to the json file containing the data

        Returns:
            json: data send to the database
        """
        url = self.URL + "ec/payloads/"
        val = self.getLocalData(jsonfile)
        DATA = {'ip':ip, 'date':date, 'type':type, 'values':val["values"]}
        json_object = self.dumpData(DATA)
        return self.post(url, json_object)

    #---------------------------------------------------
    def postDataFromSingleDeviceDict(self, ip: str, date: int, type: str, dict: dict):
        """Add data from a mutiple device to the database of a node

        Args:
            ip (str): IP of the sender device
            date (int): timestamp of the data
            type (str): type of the data
            dict (dict): dictionary containing the data

        Returns:
            json: data send to the database
        """
        url = self.URL + "ec/payloads/"
        try:
            DATA = {'ip':ip, 'date':date, 'type':type, 'values':dict["values"]}
            json_object = self.dumpData(DATA)
            return self.post(url, json_object)
        except:
            print("[Error] - Dict must have the following form: {'values': [{'id': str, 'date': int, 'parameterId': str, 'value': any}]}")
            return None
    
    #---------------------------------------------------
    def postDataFromMultipleDevice(self, jsonfile):
        """Add data from multiple devices to the database of a node

        Args:
            jsonfile (json): json file containing the data

        Returns:
            json: data send to the database
        """
        url = self.URL + "ec/payloads/multiple/"
        DATA = self.getLocalData(jsonfile)
        json_object = self.dumpData(DATA)
        return self.post(url, json_object)
    

    # COMMUNICATION PROTOCOL FUNCTIONS
    #---------------------------------------------------
    #---------------------------------------------------
    
    def postIP(self, ip: str, date: int, appname: str):
        """Send the IP of an application to the database of a node

        Args:
            ip (str): IP of the sender device
            date (int): timestamp of the data
            appname (str): name of the application
        Returns:
            json: post data send to the database
        """
        url = self.URL + "ec/appdata/appIP/"
        dict = {'values': [{'id': "0", 'date': 0, 'parameterId': "0", 'value': appname}]}
        try:
            DATA = {'ip':ip, 'date':date, 'type': 'appIP', 'values':dict["values"]}
            json_object = self.dumpData(DATA)
            return self.post(url, json_object)
        except:
            print("[Error] - Exception occur when trying to post the IP of the application")
            return url
    
    #---------------------------------------------------
    def postUse(self, ip: str, date: int, appname: str):
        """Send the CPU and RAM use of an application to the database of a node

        Args:
            ip (str): IP of the sender device
            date (int): timestamp of the data
            appname (str): name of the application
        Returns:
            json: post data send to the database
        """
        url = self.URL + "ec/appdata/appUse/"
        cpu = str(psutil.cpu_percent(4))
        ram = str(psutil.virtual_memory()[2])
        dat = {"APPNAME":appname, "CPU":cpu, "RAM": ram}
        dict = {'values': [{'id': "0", 'date': 0, 'parameterId': "0", 'value': dat}]}
        try:
            DATA = {'ip':ip, 'date':date, 'type': 'appUse', 'values':dict["values"]}
            json_object = self.dumpData(DATA)
            return self.post(url, json_object)
        except:
            print("[Error] - Exception occur when trying to post the use of the application")
            return url
        
    #---------------------------------------------------
    def postKerasModel(self, model, ip: str, date: int, appname: str):
        """Send the Keras trained model to the database of a node

        Args:
            ip (str): IP of the sender device
            date (int): timestamp of the data
            appname (str): name of the application
        Returns:
            json: post data send to the database
        """
        url = self.URL + "ec/appdata/appModel/"
        model_json = model.to_json()
        dict_struct= {'values': [{'id': "0", 'date': 0, 'parameterId': "0", 'value': model_json}]}
        
        weights = []
        for layer in model.layers: 
            weights.append([layer.get_weights()[0].tolist(), layer.get_weights()[1].tolist()])
        
        dict_weight= {'values': [{'id': "0", 'date': 0, 'parameterId': "0", 'value': weights}]}
        try:
            DATASTRUCT = {'ip':ip, 'date':date, 'type': 'model_struct', 'values':dict_struct["values"]}
            json_object_struct = self.dumpData(DATASTRUCT)
            resstruct = self.post(url, json_object_struct)
            DATAWEIGHT = {'ip':ip, 'date':date, 'type': 'model_weight', 'values':dict_weight["values"]}
            json_object_weight = self.dumpData(DATAWEIGHT)
            resweight = self.post(url, json_object_weight)
            return resstruct, resweight
        except:
            print("[Error] - Exception occur when trying to post the model of the application")
            return url    
    
    #---------------------------------------------------
    def deleteAppIPbyName(self, name):
        """Delete the IP of an application from the database of a node

        Args:
            name (str): name of the application

        Returns:
            json: data send to the database
        """
        url = self.URL + "ec/appdata/appIP/?type=" + name
        return self.delete(url)
    
    #---------------------------------------------------
    def getAppIPbyName(self, name):
        """Returns the IP of an application in the database of a node based on its name

        Args:
            name (str): name of the application

        Returns:
            json: data send to the database
        """
        url = self.URL + "ec/appdata/appIP/?type=" + name
        return self.get(url)

    #---------------------------------------------------
    def getAppUsebyName(self, name):
        """Returns the IP of an application in the database of a node based on its name

        Args:
            name (str): name of the application

        Returns:
            json: data send to the database
        """
        url = self.URL + "ec/appdata/appUse/?type=" + name
        return self.get(url)

    #---------------------------------------------------
    def getKerasModel(self, ip):
        """Returns the IP of an application in the database of a node based on its name

        Args:
            name (str): name of the application

        Returns:
            json: data send to the database
        """
        url = self.URL + "ec/appdata/appModel/?type=" + ip
        res = self.get(url)
        
        model = keras.models.model_from_json(res['data'][0])
        weights = res["data"][1]
        for i in range(0,len(weights)):
            wg0 = np.array(weights[i][0], dtype=object)
            wg1 = np.array(weights[i][1], dtype=object)
            model.layers[i].set_weights([wg0, wg1])
        return model
    
    
    # GENERIC FUNCTIONS
    #---------------------------------------------------
    #---------------------------------------------------
    
    def post(self, url, json_object):
        """Generic function to post data to the database

        Args:
            url (str): particular url to post the data
            json_object (json): the data to post

        Returns:
            json: data send to the database
        """
        try:
            resp = requests.post(url=url, headers=self.headers, data=json_object)
            if(resp.status_code in [204,200,201]):
                return resp.json()
            else:
                return None
        except Exception as inst:
            print("[Error] - ", type(inst))
            return None
    
    #---------------------------------------------------
    def delete(self, url):
        """Generic function to delete data from the database
        
        Args:
            url (str): particular url to delete the data
        
        Returns:
            json: data delete from the database 
        """
        try:
            resp = requests.delete(url=url, headers=self.headers)
            if(resp.status_code in [204,200,201]):
                return resp.json()
            else:
                return None
        except Exception as inst:
            print("[Error] - ", type(inst))
            return None
    
    #---------------------------------------------------
    def get(self, url):
        """Generic function to get data from the database

        Args:
            url (str): particular url to get the data

        Returns:
            json: data get from the database
        """
        try:
            resp = requests.get(url=url, headers=self.headers)
            if(resp.status_code in [204,200,201]):
                return resp.json()
            else:
                return None
        except Exception as inst:
            print("[Error] - ", type(inst))
            return None
    
    # UTILITY FUNCTIONS
    #---------------------------------------------------
    #---------------------------------------------------
    
    def getLocalData(self, path):
        """Returns the data of a json file

        Args:
            path (str): path to the json file

        Returns:
            dict: data of the json file
        """
        f = open(path)
        values = json.load(f)
        return values
    
    def dumpData(self, dict):
        """Send dictionary to json format

        Args:
            dict (dict): dictionary to send to json format

        Returns:
            json: dictionary in json format
        """
        return json.dumps(dict, indent = 4)
    