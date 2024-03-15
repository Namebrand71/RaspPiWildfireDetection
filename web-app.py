import matplotlib.pyplot as plt
from flask import Flask, render_template
import os
import requests
php_script_url = 'http://localhost/polling.php'
app = Flask(__name__, template_folder='templates')
categories = ['sec1', 'sec2', 'primary', 'avg']


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body):
    # Sender email credentials
    sender_email = "havasuwildfiredetection@gmail.com"
    sender_password = "tdhu jneh ilfq giyl"

    # Recipient email
    recipient_email = "brandontlawrence@gmail.com"

    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Attach the body to the email
    message.attach(MIMEText(body, "plain"))

    # Connect to the SMTP server (Gmail example)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        # Log in to the sender email account
        server.login(sender_email, sender_password)
        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())
		
def generate_plots():
		
		get_params = {'table': 'sensor_readings1'}  # Change the table name as needed
		get_response1 = requests.get(php_script_url, params=get_params)
		data1 = get_response1.json()
		data1['temperature'] = float(data1['temperature'])
		data1['humidity'] = float(data1['humidity'])
		data1['wind_speed'] = float(data1['wind_speed'])
		data1['soil_moisture'] = float(data1['soil_moisture'])
		get_params = {'table': 'sensor_readings2'}  # Change the table name as needed
		get_response2 = requests.get(php_script_url, params=get_params)
		data2 = get_response2.json()
		data2['temperature'] = float(data2['temperature'])
		data2['humidity'] = float(data2['humidity'])
		data2['wind_speed'] = float(data2['wind_speed'])
		data2['soil_moisture'] = float(data2['soil_moisture'])
		get_params = {'table': 'sensor_readings3'}  # Change the table name as needed
		get_response3 = requests.get(php_script_url, params=get_params)
		data3 = get_response3.json()
		data3['temperature'] = float(data3['temperature'])
		data3['humidity'] = float(data3['humidity'])
		data3['wind_speed'] = float(data3['wind_speed'])
		data3['soil_moisture'] = float(data3['soil_moisture'])

		data = [data1['temperature'],data2['temperature'],data3['temperature'],((data1['temperature'] + data2['temperature'] + data3['temperature'])/3)]
		plt.figure()
		bars = plt.bar(categories, data, color=['blue', 'green', 'orange', 'red'])
		plt.title('temperature')
		plt.xlabel('X-axis')
		plt.ylabel('Y-axis')
		plt.grid(True)
		plt.savefig('static/graph1.png')
		
		data = [data1['humidity'],data2['humidity'],data3['humidity'],((data1['humidity'] + data2['humidity'] + data3['humidity'])/3)]
		plt.figure()
		bars = plt.bar(categories, data, color=['blue', 'green', 'orange', 'red'])
		plt.title('humidity')
		plt.xlabel('X-axis')
		plt.ylabel('Y-axis')
		plt.grid(True)
		plt.savefig('static/graph2.png')
		
		data = [data1['wind_speed'],data2['wind_speed'],data3['wind_speed'],((data1['wind_speed'] + data2['wind_speed'] + data3['wind_speed'])/3)]
		plt.figure()
		bars = plt.bar(categories, data, color=['blue', 'green', 'orange', 'red'])
		plt.title('wind_speed')
		plt.xlabel('X-axis')
		plt.ylabel('Y-axis')
		plt.grid(True)
		plt.savefig('static/graph3.png')
		
		data = [data1['soil_moisture'],data2['soil_moisture'],data3['soil_moisture'],((data1['soil_moisture'] + data2['soil_moisture'] + data3['soil_moisture'])/3)]
		plt.figure()
		bars = plt.bar(categories, data, color=['blue', 'green', 'orange', 'red'])
		plt.title('soil_moisture')
		plt.xlabel('X-axis')
		plt.ylabel('Y-axis')
		plt.grid(True)
		plt.savefig('static/graph4.png')

@app.route('/')
@app.route('/home')
def index():
    generate_plots()
    
    if 0:
        subject = "WILDFIRE LEVEL MEDIUM"
        body = "We detected a problem"
        send_email(subject, body)
    elif 0:
        subject = "WILDFIRE LEVEL HIGH"
        body = "We detected a problem"
        send_email(subject, body)
		
    return render_template('page.html')

if __name__ == '__main__':

    
    app.run(host='0.0.0.0', port=30006, debug=True)
	
	
