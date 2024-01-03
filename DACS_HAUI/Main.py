import smtplib
import os
import sys
import time
import M1_L5_LCD_Fun as LCD
from bluepy import sensortag
import M1_L7_Pressure_Fun as Pres
import requests
import paho.mqtt.client as mqtt
import csv

LCD.LCD_init()
LCD.LCD_clear()

#Khoi tao gia tri 
HudData = 0
TempData = 0
PresData = 0
LuxData = 0

# Email sender infor
sender_email = 'hangminhnguyen676@gmail.com'
sender_password = 'Hang1452005'

# Email receiver infor
receiver_email = 'tuantuan140120@gmail.com'

# Email infor
subject = 'Email subject'
message = 'Email content'

api_key = "db573acb1d90981a42358c1b08024c9f"
city = "Hanoi, Vietnam"

print "\nPreparing to connect..."
print "You might need to press the side button on Sensor Tag within 2 seconds..."
time.sleep(2.0)

#Khoi tao cam bien
tag = sensortag.SensorTag('54:6C:0E:53:2C:0A')
tag.humidity.enable()
tag.lightmeter.enable()

#Gui email
def SendEmail(sender_email, sender_password, receiver_email, subject, message):
  server = smtplib.SMTP('smtp.office365.com', 587)
  server.starttls()

  # Login
  server.login(sender_email, sender_password)

  # Create Email content
  email_message = "Subject: " + str(subject) + "\n" + str(message)
  email_message = email_message.encode('utf-8')

  # Send email
  server.sendmail(sender_email, receiver_email, email_message)

  # Close SMTP
  server.quit()

#Lay du lieu thoi tiet tai khu vuc Ha Noi bang API openweathermap
def GetWeather(city, api_key):
  base_url = "http://api.openweathermap.org/data/2.5/weather"
  params = {"q": city,"appid": api_key}
  while 1:
    response = requests.get(base_url, params=params)
    data = response.json()
    if response.status_code == 200:
      weather = data["weather"][0]["description"]
      temperature = data["main"]["temp"]
      humidity = data["main"]["humidity"]
      print("Kinh do: " ,data['coord']['lon'])
      print("Vi do: " ,data['coord']['lat'])
      print("Thoi tiet tai " + str(city) + ": " + str(weather))
      break

#Luu du lieu cam bien vao file data.csv
savedata = []
def SaveData(row):
  savedata.append(row)
  with open('data.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(savedata)

#Vong lap chay chuong trinh
while (1):
	tag.waitForNotifications(1.0)
	
    #Thu thap du lieu thu duoc tai cam bien
	data = tag.humidity.read()
    #Cam bien nhiet do
	TempData = abs(data[0])
	TempData = round(TempData, 1)
    #Cam bien do am
	HudData = abs(data[1])
	HudData = round(HudData, 1)
    #Cam bien anh sang
	data1 = tag.lightmeter.read()
	LuxData = data1
	LuxData = round(LuxData)
    #Cam bien ap suat
	PresData = Pres.Pressure_read()[0]
	
    #Luu du lieu
	row = [TempData, HudData, LuxData, PresData]
	SaveData(row)
	
    #In du lieu cam bien ra man hinh va LCD
	text = "Nhiet do: " + str(TempData) + " C\nDo am: " + str(HudData) + "\nAp suat: " + str(PresData) + "\nCuong do a/s: " + str(LuxData) + " LUX"
	print text + "\n"
	LCD.LCD_print(str(TempData) + "  " + str(HudData))
	LCD.LCD_print2(str(PresData) + "  " + str(LuxData))
    
    #Kiem tra neu cuong do anh sang vuot qua nguong
	if LuxData > 500:
	  SendEmail(sender_email, sender_password, receiver_email, subject, message)
	  GetWeather(city, api_key)
	
	time.sleep(1.0)
tag.disconnect()
del tag