import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import requests
php_script_url = 'http://localhost/polling.php'
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

if __name__ == "__main__":

    # Simulating some data and checking the threshold
    while 1:
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
    
        tempavg = ((data1['temperature'] + data2['temperature'] + data3['temperature'])/3)
        humidavg = ((data1['humidity'] + data2['humidity'] + data3['humidity'])/3)
        windavg = ((data1['wind_speed'] + data2['wind_speed'] + data3['wind_speed'])/3)
        soilavg = ((data1['soil_moisture'] + data2['soil_moisture'] + data3['soil_moisture'])/3)
		
		
		
        tempbool = (tempavg > 30)
        humidbool = (humidavg < 16)
        windbool = (windavg > 24)
        soilbool = (soilavg < 500)
        threshold = tempbool + windbool + humidbool + soilbool
		
        print(threshold)
        if 1 == threshold:
            subject = "THREAT LEVEL LOW"
            body = f"tempthresh = {tempbool}, humidthresh = {humidbool}, windthresh = {windbool}, soilthresh = {soilbool}"
            send_email(subject, body)
        elif 2 == threshold:
            subject = "THREAT LEVEL MEDIUM"
            body = f"tempthresh = {tempbool}, humidthresh = {humidbool}, windthresh = {windbool}, soilthresh = {soilbool}"
            send_email(subject, body)
        elif threshold >= 3:
            subject = "THREAT LEVEL HIGH"
            body = f"tempthresh = {tempbool}, humidthresh = {humidbool}, windthresh = {windbool}, soilthresh = {soilbool}"
            send_email(subject, body)
			
        time.sleep(30);