# multiconn-server.py

from copy import error
from math import e
import sys
import socket
import selectors
import types
import time
import matplotlib.pyplot as plt
import numpy as np
import pickle
import json
import requests
import subprocess 
sel = selectors.DefaultSelector()

import board
import busio
import time
import adafruit_sht31d
from adafruit_seesaw.seesaw import Seesaw

from simpleio import map_range
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from time import strftime
from datetime import datetime
from pytz import timezone

# ...

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

def eth0_down():
    command = "sudo ifconfig eth0 down"
    try:
        # Run the command with subprocess
        subprocess.run(command, shell=True, check=True)
        print("Command executed successfully: sudo ifup eth0")
    except subprocess.CalledProcessError as e:
        # Handle any errors
        print(f"Error executing command: {command}")
        print(f"Error details: {e}")

def eth0_up():
    command = "sudo ifconfig eth0 up"
    try:
        # Run the command with subprocess
        subprocess.run(command, shell=True, check=True)
        print("Command executed successfully: sudo ifup eth0")
    except subprocess.CalledProcessError as e:
        # Handle any errors
        print(f"Error executing command: {command}")
        print(f"Error details: {e}")

eth0_up()

plotnum = 1
# Categories
categories = ["Sec1", "Sec2", "Primary", "Avg"]
colors = ['blue', 'red', 'black', 'green']
# Initial data generation (random values between 1 and 100)
data = {
    "Temperature": [20,20,20,30],
    "Humidity": [20,20,20,65],
    "Soil Moisture": [300,300,300,1100],
    "Wind Speed": [0.1,0.1,0.1,3.1]
}

# Creating subplots
fig, axs = plt.subplots(2, 2, figsize=(10, 8))
fig.suptitle("Scatter Plots")

# Scatter plot initialization
scatter1 = axs[0, 0].scatter(range(len(categories)), data["Temperature"], color=colors)
axs[0, 0].set_title('Temperature')
scatter2 = axs[0, 1].scatter(range(len(categories)), data["Humidity"], color=colors)
axs[0, 1].set_title('Humidity')
scatter3 = axs[1, 0].scatter(range(len(categories)), data["Soil Moisture"], color=colors)
axs[1, 0].set_title('Soil Moisture')
scatter4 = axs[1, 1].scatter(range(len(categories)), data["Wind Speed"], color=colors)
axs[1, 1].set_title('Wind Speed')

# Setting labels for x-axis and y-axis
for ax in axs.flat:
    ax.set(xticks=range(len(categories)), xticklabels=categories, ylabel='Values')


j=0


sec1_temp,sec2_temp,primary_temp,avg_temp=0,0,0,0
sec1_humid,sec2_humid,primary_humid,avg_humid=0,0,0,0
sec1_moist,sec2_moist,primary_moist,avg_moist=0,0,0,0
sec1_wind,sec2_wind,primary_wind,avg_wind=0,0,0,0

def adc_to_wind_speed(val):
    return map_range(val, 0.4, 2.0, 0.0, 32.4)
    
def plot_temp():
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    avg_temp = ((sec1_temp + sec2_temp + primary_temp) / 3)
    data["Temperature"] = [sec1_temp,sec2_temp,primary_temp,avg_temp]
    scatter1.set_offsets(np.column_stack((np.arange(len(categories)), data["Temperature"])))
def plot_humid():
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    avg_humid = ((sec1_humid + sec2_humid + primary_humid) / 3)
    data["Humidity"] = [sec1_humid,sec2_humid,primary_humid,avg_humid]
    scatter2.set_offsets(np.column_stack((np.arange(len(categories)), data["Humidity"])))
def plot_soil_moisture():
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    avg_moist = ((sec1_moist + sec2_moist + primary_moist) / 3)
    data["Soil Moisture"] = [sec1_moist,sec2_moist,primary_moist,avg_moist]
    scatter3.set_offsets(np.column_stack((np.arange(len(categories)), data["Soil Moisture"])))
def plot_wind_speed():
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    avg_wind = ((sec1_wind + sec2_wind + primary_wind) / 3)
    data["Wind Speed"] = [sec1_wind,sec2_wind,primary_wind,avg_wind]
    scatter4.set_offsets(np.column_stack((np.arange(len(categories)), data["Wind Speed"])))


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"",i=0)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask, num):
    global j
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    sock = key.fileobj
    data = key.data
    message = "Handle Request {}".format(data.i)
    message_bytes = message.encode('utf-8')
    data.outb = message_bytes

    

    data.i=data.i+1
    try:
        print(f"Sending {data.outb!r} to {data.addr}")
        sent = sock.send(data.outb)  # Should be ready to write

        data.outb = data.outb[sent:]

    except (ConnectionResetError, BrokenPipeError,ValueError, OSError):
        return
    time.sleep(1)
    try:
        recv_data = sock.recv(2040)  # Should be ready to read
        if recv_data:
            temprecv_data = pickle.loads(recv_data)
            list_data = list(temprecv_data)
            print(list_data[0], list_data[1])
            if num == 1:
                sec1_temp = list_data[0]
                sec1_humid = list_data[1]
                sec1_moist = list_data[2]
                sec1_wind = list_data[3]
            elif num == 2:
                sec2_temp = list_data[0]
                sec2_humid = list_data[1]
                sec2_moist = list_data[2]
                sec2_wind = list_data[3]
            else:
                print()
            plt.pause(1)
            time.sleep(1)
        else:
            print(f"Closing connection {data.addr}")
            sel.unregister(sock)
            sock.close()
    except(ConnectionResetError,BrokenPipeError,ValueError,OSError) as err:
        print(f"Exception,Closing connection {data.addr} and {err}")
        sel.unregister(sock)
        sock.close()
        time.sleep(2)


db_url = 'http://169.233.134.199/polling.php'

# Data to be sent for multiple tables
data_to_server = [
    {
        'table': 'sensor_readings1',
        'temperature': 25.5,
        'humidity': 50.2,
        'windSpeed': 10.3,
        'soilMoisture': 35.7
    },
    {
        'table': 'sensor_readings2',
        'temperature': 26.0,
        'humidity': 48.5,
        'windSpeed': 11.2,
        'soilMoisture': 34.2
    },
    {
        'table': 'sensor_readings3',
        'temperature': 24.8,
        'humidity': 51.8,
        'windSpeed': 9.5,
        'soilMoisture': 36.5
    }
]
        
count = 0

try:
        # Initialize I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Initialize SHT30 temperature sensor
    sht30 = adafruit_sht31d.SHT31D(i2c)

    # Initialize STEMMA Soil Sensor
    seesaw = Seesaw(i2c, addr=0x36)

    ads = ADS.ADS1015(i2c)
    chan = AnalogIn(ads, ADS.P0)

    # wait for two connections
    while count < 2:
        events = sel.select()
        for key, mask in events:
            # print("key: ", key, "mask: ", mask)
            if key.data is None: 
                accept_wrapper(key.fileobj)
            else:
                if count == 0:
                    key1 = key
                    mask1 = mask
                    count = count + 1
                    print('one connection made')
                elif count == 1:
                    key2 = key
                    mask2 = mask
                    count = count + 1
    print('two connection made')
    #MAIN LOOP
    headers = {'Content-Type': 'application/json'}
    while True:
        primary_temp = int(sht30.temperature)
        primary_humid = int(sht30.relative_humidity)
        primary_wind = (adc_to_wind_speed(chan.voltage))
        primary_moist = int(seesaw.moisture_read())

        service_connection(key1, mask1, 1)

        service_connection(key2, mask2, 2)

        plot_humid()
        plot_soil_moisture()
        plot_temp()
        plot_wind_speed()
        save = 'polling-plot-' + str(plotnum) + '.png'
        
        plt.savefig(save)
        plotnum = plotnum + 1
        i = 0
        for table in data_to_server:
            if i == 0:
                table['temperature'] = sec1_temp
                table['humidity'] = sec1_humid
                table['windSpeed'] = sec1_wind
                table['soilMoisture'] = sec1_moist
            elif i == 1:
                table['temperature'] = sec2_temp
                table['humidity'] = sec2_humid
                table['windSpeed'] = sec2_wind
                table['soilMoisture'] = sec2_moist
            elif i == 2:
                table['temperature'] = primary_temp
                table['humidity'] = primary_humid
                table['windSpeed'] = primary_wind
                table['soilMoisture'] = primary_moist
            i = i+1
        response = requests.post(db_url, data=json.dumps(data_to_server), headers=headers)

		# Printing the response
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.text)

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()

