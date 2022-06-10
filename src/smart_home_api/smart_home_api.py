import requests
from ..ESP8266.ESP8266_01_Types import *
from ..ESP8266.ESP8266_01_device import ESP8266_01_Type

BASE_URL = "http://localhost:8000/api/"

def check_device_class(hwid):
    res = None
    req_params = {'hwid': hwid}
    api_method = "check_device_class"
    print(req_params)
    try:
        response = requests.post(BASE_URL+api_method,data=req_params,timeout=4)
        if response.status_code == 200:
            data = response.json()
            # print(data)
            # res = data['device_class']
            # res = ESP8266_01_Type['Relay_Device']
            res = ESP8266_01_Type(data['device_class'])
            print("Res: "+str(res))
        elif response.status_code == 400:
            # print("check_device_class")
            print("Bad request")
            # print(response.json())
        else:
            print("Random error")
    except (requests.ConnectionError) as err:
        print("Django API not working")
    return res

def check_relay_trigger(hwid,bus):
    res = None
    try:
        req_params = {'hwid': hwid, 'bus':bus}
        api_method = "check_relay_trigger"

        response = requests.post(BASE_URL+api_method,data=req_params)
        if response.status_code == 200:
            print(req_params)
            data = response.json()
            res = data['fulfilled']
            print(data['fulfilled'])
        elif response.status_code == 400:
            print("Bad request")
            print(response.json())
        else:
            print("Random error")
    except (requests.ConnectionError) as err:
        print("Django API not working")
    return res

def add_sensor_log(hwid,data_type,value):
    res = None
    try:
        req_params = {'hwid': hwid, 'data_type':data_type,'value':value}
        api_method = "add_sensor_log"
        response = requests.post(BASE_URL+api_method,data=req_params)
        if response.status_code == 200:
            print(response.json())
            print("Added sensor log")
        elif response.status_code == 400:
            print("Bad request")
            print(response.json())
        else:
            print("Random error")
    except (requests.ConnectionError) as err:
        print("Django API not working")
    return res

