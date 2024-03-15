from copy import error
from math import e
import sys 
import socket 
import time
import matplotlib.pyplot as plt
import numpy as np
import pickle
import types
import subprocess
import requests
import json
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

port = int(sys.argv[2])
host = "192.168.7.3"
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(True)
plotnum = 1
# Categories
categories = ["Sec1", "Sec2", "Primary", "Avg"]
colors = ['blue', 'red', 'black', 'green']
# Initial data generation (random values between 1 and 100)
plotdata = {
    "Temperature": [20,20,20,30],
    "Humidity": [20,20,20,65],
    "Soil Moisture": [300,300,300,1100],
    "Wind Speed": [0.1,0.1,0.1,3.1]
}

# Creating subplots
fig, axs = plt.subplots(2, 2, figsize=(10, 8))
fig.suptitle("Scatter Plots")

# Scatter plot initialization
scatter1 = axs[0, 0].scatter(range(len(categories)), plotdata["Temperature"], color=colors)
axs[0, 0].set_title('Temperature')
scatter2 = axs[0, 1].scatter(range(len(categories)), plotdata["Humidity"], color=colors)
axs[0, 1].set_title('Humidity')
scatter3 = axs[1, 0].scatter(range(len(categories)), plotdata["Soil Moisture"], color=colors)
axs[1, 0].set_title('Soil Moisture')
scatter4 = axs[1, 1].scatter(range(len(categories)), plotdata["Wind Speed"], color=colors)
axs[1, 1].set_title('Wind Speed')

# Setting labels for x-axis and y-axis
for ax in axs.flat:
    ax.set(xticks=range(len(categories)), xticklabels=categories, ylabel='Values')

sec1_temp,sec2_temp,primary_temp,avg_temp=0,0,0,0
sec1_humid,sec2_humid,primary_humid,avg_humid=0,0,0,0
sec1_moist,sec2_moist,primary_moist,avg_moist=0,0,0,0
sec1_wind,sec2_wind,primary_wind,avg_wind=0,0,0,0
db_url = 'http://169.233.134.199/polling.php'
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


def plot_temp():
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    avg_temp = ((sec1_temp + sec2_temp + primary_temp) / 3)
    plotdata["Temperature"] = [sec1_temp,sec2_temp,primary_temp,avg_temp]
    scatter1.set_offsets(np.column_stack((np.arange(len(categories)), plotdata["Temperature"])))
    print('we he')
def plot_humid():
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    avg_humid = ((sec1_humid + sec2_humid + primary_humid) / 3)
    plotdata["Humidity"] = [sec1_humid,sec2_humid,primary_humid,avg_humid]
    scatter2.set_offsets(np.column_stack((np.arange(len(categories)), plotdata["Humidity"])))
def plot_soil_moisture():
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    avg_moist = ((sec1_moist + sec2_moist + primary_moist) / 3)
    plotdata["Soil Moisture"] = [sec1_moist,sec2_moist,primary_moist,avg_moist]
    scatter3.set_offsets(np.column_stack((np.arange(len(categories)), plotdata["Soil Moisture"])))
    print('we here')
def plot_wind_speed():
    global sec1_temp,sec2_temp,primary_temp,avg_temp
    global sec1_humid,sec2_humid,primary_humid,avg_humid
    global sec1_moist,sec2_moist,primary_moist,avg_moist
    global sec1_wind,sec2_wind,primary_wind,avg_wind
    avg_wind = ((sec1_wind + sec2_wind + primary_wind) / 3)
    plotdata["Wind Speed"] = [sec1_wind,sec2_wind,primary_wind,avg_wind]
    scatter4.set_offsets(np.column_stack((np.arange(len(categories)), plotdata["Wind Speed"])))

def adc_to_wind_speed(val):
    return map_range(val, 0.4, 2.0, 0.0, 32.4)

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"",i=0)
    #events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #sel.register(conn, events, data=data)

def send_message(client_host, client_port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((client_host, client_port))
        client_socket.sendall(message)
        print(f"sent message to {client_host}, {client_port}")
def eth0_down():
    command = "sudo ifconfig eth0 down"
    try:
        # Run the command with subprocess
        subprocess.run(command, shell=True, check=True)
        print("Command executed successfully: sudo ifdown eth0")
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


clientport = int(sys.argv[3])
forward = "192.168.9.2"
mode = int(sys.argv[1])
if (mode == 1):
    communication = "start"
    message = "hello from brooke"
elif (mode == 2):
    communication = "listen"
elif (mode == 3):
    communication = "listen and do"
    message = "restart communication"
headers = {'Content-Type': 'application/json'}
eth0_down()
while True:
    i2c = busio.I2C(board.SCL, board.SDA)
    sht30 = adafruit_sht31d.SHT31D(i2c)
    seesaw = Seesaw(i2c, addr=0x36)
    ads = ADS.ADS1015(i2c)
    chan = AnalogIn(ads, ADS.P0)
    #initializations of all the board components
    while (communication == "start"):
        try:
            if (mode == 1):
                #sensor data stuff here
                primary_temp = int(sht30.temperature)
                primary_humidity = int(sht30.relative_humidity)
                primary_wind = int(adc_to_wind_speed(chan.voltage))
                primary_moist = int(seesaw.moisture_read())
                alldata = [primary_temp, primary_humidity, primary_wind, primary_moist]
                serialized_list = pickle.dumps(alldata)
                send_message(forward, clientport, serialized_list)
                print(f"sending message: {alldata}")
            elif (mode == 2):
                sec1_temp = int(sht30.temperature)
                sec1_humid = int(sht30.relative_humidity)
                sec1_wind = int(adc_to_wind_speed(chan.voltage))
                sec1_moist = int(seesaw.moisture_read())
                currdata = pickle.loads(message)
                curr = list(currdata)
                curr.append(sec1_temp)
                curr.append(sec1_humid)
                curr.append(sec1_wind)
                curr.append(sec1_moist)
                serialized_currdata = pickle.dumps(curr)
                send_message(forward, clientport, serialized_currdata)
                print(f"sending message: {message}")
            elif (mode == 3):
                send_message(forward, clientport, message)
                print("sending message to initiator")
            time.sleep(2)
        except ConnectionRefusedError:
            time.sleep(2)
        else:
            if (mode == 3):
                communication = "listen and do"
            else:    
                communication = "listen"

    while (communication == "listen"):
        client_sock, addr = lsock.accept()
        data = client_sock.recv(4096)
        
        if not data:
            # If no data, the client has closed the connection
            print(f"Connection closed by {addr}")
        message = data
        communication = "start"
        print(f"Received: pickle.loads(data)")
    while (communication == "listen and do"):
        client_sock, addr = lsock.accept()
        data = client_sock.recv(4096)
        thirdpi_temp = int(sht30.temperature)
        thirdpi_humidity = int(sht30.relative_humidity)
        thirdpi_wind = int(adc_to_wind_speed(chan.voltage))
        thirdpi_moist = int(seesaw.moisture_read())
        currdata = pickle.loads(data)
        finaldata = list(currdata)
        print('this is final data', finaldata)
        if not data:
            print(f"connection closed by{addr}")
        #do the graphing here
        #the deserialized data is the dictionary from the (mode == 1) if statement above
        #elements = currdata['temperature3']

        sec1_temp,sec2_temp,primary_temp=finaldata[4],thirdpi_temp,finaldata[0]
        sec1_humid,sec2_humid,primary_humid=finaldata[5],thirdpi_humidity,finaldata[1]
        sec1_wind,sec2_wind,primary_wind=finaldata[6],thirdpi_wind,finaldata[2]
        sec1_moist,sec2_moist,primary_moist=finaldata[7],thirdpi_moist,finaldata[3]
        
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
        eth0_up()
        time.sleep(10)
        response = requests.post(db_url, data=json.dumps(data_to_server), headers=headers)
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.text)
        eth0_down()
        print(sec1_temp,sec2_temp,primary_temp,sec1_humid,sec2_humid,primary_humid,sec1_wind,sec2_wind,primary_wind,sec1_moist,sec2_moist,primary_moist)
        plot_humid()
        plot_soil_moisture()
        plot_temp()
        plot_wind_speed()
        plt.pause(1)
        save = 'token-plot-' + str(plotnum) + '.png'
        
        plt.savefig(save)
        plotnum = plotnum + 1
        message = "start the whole process"
        message = message.encode()
        communication = "start"


