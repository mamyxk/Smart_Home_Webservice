import asyncio
from configparser import SectionProxy
import websockets
import datetime
from queue import Queue
import struct

from .ESP8266_01_Types import *
from ..smart_home_api.smart_home_api import *

TURN_ON : bytes = b'\xf1'
TURNN_OFF : bytes = b'\xf0'


RESPONSE_ON : bytes = b'\x71'
RESPONSE_OFF : bytes = b'\x70'

SOCKET_RELAY_DEVICE_TIMEOUT = 10.0
DEFAULT_TIME_CHECK_INTERVAL = datetime.timedelta(minutes=5)


class ESP8266_01():
    device_hwid: int
    device_ip: str
    commands: Queue
    kill_condition: bool
    wsocket : websockets
    time_last_ping : datetime.datetime
    time_last_status : datetime.datetime
    ping_interval : datetime.timedelta
    status_interval : datetime.timedelta


    REQUEST_WHO_HEADER : bytes = b'\x00'
    REQUEST_STATUS_HEADER : bytes = b'\x01'
    REQUEST_PING_HEADER : bytes = b'\xff'

    RESPONSE_WHO_HEADER : bytes = b'\x00'
    RESPONSE_STATUS_HEADER : bytes = b'\x01'
    RESPONSE_ACKNOWLEDGED : bytes = b'\x7f'

    DEVICE_TIMEOUT = 20.0

    def __init__(self, device_id):
        self.device_hwid = device_id
        self.commands = Queue(maxsize=20)
        self.kill_condition = False
        self.time_last_ping = datetime.datetime.now()
        self.ping_interval = datetime.timedelta(seconds=30)
        self.time_last_status = datetime.datetime.now()
        self.status_interval = datetime.timedelta(seconds=4)
        # self.add_command_request_ping()
        self.add_command_request_status()
        

    def add_command_request_ping(self):
        self.commands.put(self.REQUEST_PING_HEADER+self.RESPONSE_ACKNOWLEDGED)
    
    def add_command_request_status(self):
        self.commands.put(self.RESPONSE_STATUS_HEADER+self.RESPONSE_ACKNOWLEDGED)

    def handle_data(self,payload):
        print("Handling data")
        header = payload[0:1]
        None

    def send_data(self):
        for command in self.commands.queue:
            print(command)

    def get_commands(self):
        return self.commands

    def update_commands(self):
        if datetime.datetime.now() - self.time_last_ping > self.ping_interval:
            # self.commands.put(self.REQUEST_PING_HEADER)
            None
            # Commands append check ping
        if datetime.datetime.now() - self.time_last_status > self.status_interval:
            self.commands.put(self.REQUEST_STATUS_HEADER+self.RESPONSE_ACKNOWLEDGED)


    def get_hwid(data):
        if data[0:1] == ESP8266_01.RESPONSE_WHO_HEADER:
            hwid = int.from_bytes(data[1:2],'big')
            return hwid
        else:
            return None

class Commands(Enum):
    READ_STATE = 1
    SET_STATE = 2

class Relay_Device(ESP8266_01):
    connected : bool
    requested_state: bool
    current_state: bool

    REQUEST_SET_STATE_HEADER : bytes = b'\x02'

    STATE_ON : bytes = b'\x71'
    STATE_OFF : bytes = b'\x70'

    time_last_requested_check : datetime.datetime
    requested_check_interval : datetime.timedelta
    
    
    def __init__(self, device_hwid, bus_count):
        ESP8266_01.__init__(self,device_hwid)
        self.requested_state = False
        self.current_state = False
        self.bus_count = bus_count
        self.time_check_interval = datetime.timedelta(seconds=10)
        print(f"Created Relay_Device with hwid: {device_hwid} buses: {bus_count}")
        self.connected = True
        self.time_last_requested_check = datetime.datetime.now()
        self.requested_check_interval = datetime.timedelta(seconds=5)

    def handle_data(self,payload):
        # print("Handling data")
        # print(payload)
        header = payload[0:1]
        if header == self.RESPONSE_STATUS_HEADER:
            status_data = payload[1:2]
            if status_data == self.STATE_ON:
                print("Relay is ON")
                self.current_state = True
            elif status_data == self.STATE_OFF:
                print("Relay is off")
                self.current_state = False

    def set_requested_state(self,state):
        self.requested_state = state

    def read_requested_state(self):
        state = check_relay_trigger(self.device_hwid,0)
        if state != None:
            self.requested_state = state

    def add_command_set_status(self):
        if self.requested_state:
            command = self.REQUEST_SET_STATE_HEADER+self.STATE_ON+self.RESPONSE_ACKNOWLEDGED
            print("Setting on")
            self.commands.put(command)
        else:
            command = self.REQUEST_SET_STATE_HEADER+self.STATE_OFF+self.RESPONSE_ACKNOWLEDGED
            print("Settings off")
            self.commands.put(command)

    def update_commands(self):
        if datetime.datetime.now() - self.time_last_requested_check > self.requested_check_interval:
            print("New requested state")
            self.requested_state = check_relay_trigger(self.device_hwid,0)
            None
            # Check requested state
        if self.requested_state != self.current_state:
            self.add_command_set_status()
        super().update_commands()


class DHT22_Device(ESP8266_01):
    connected : bool
    def __init__(self, device_hwid):
        ESP8266_01.__init__(self,device_hwid)
        print(f"Created DHT22_Device with hwid: {device_hwid}")
        self.connected = True

    # Its enough, super() has get status
    def update_commands(self):
        super().update_commands()

    # When received temperature and humidity, send it to django
    def handle_data(self,payload):
        header = payload[0:1]
        if header == self.RESPONSE_STATUS_HEADER:
            bytes_temp = payload[1:5]
            bytes_humi = payload[5:9]
            temperature = struct.unpack('<f',bytes_temp)[0]
            humidity = struct.unpack('<f',bytes_humi)[0]
            # print(f"Receivec Status from HWID: {self.device_hwid}")
            # print("Temperature: "+str(temperature))
            # print("Humidity: "+str(humidity))
            add_sensor_log(self.device_hwid,1,temperature)
            add_sensor_log(self.device_hwid,2,humidity)

