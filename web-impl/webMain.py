import network
import socket
from time import sleep
import machine
from machine import Pin
import gc


onboard = Pin("LED", Pin.OUT, value=0)
#TEMP VARS
test = "start"
minTemp = 0

ssid = 'SET'       #Set access point name 
password = 'Grunklestan'      #Set your access point password
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)            #activating

while ap.active() == False:
  pass
print('Connection is successful')
print(ap.ifconfig())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

def get_html(html_name,css_name):
   with open(html_name, 'r') as file:
      html = file.read().format(Current_temp=test,MIN=minTemp,MAX="max",outdoor_temp="outdoor",light_mode="light mode")
      file.close()
   with open(css_name, 'r') as file1:
      css = file1.read()
      file1.close()
   input_file = str(html)+"<style>" +str(css)+ "</style>"
   return input_file

def webpage():
    html = get_html('index.html','styles.css')
    return str(html)

while True:
    gc.collect()
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)
    try:
        request = request.split()[1]
    except IndexError:
        pass
    if request == '/mintempup?':
        test='IT WORKED!'
        minTemp+=1
    if request == '/mintempdown?':
        minTemp-=1
    elif request == '/lightoff?':
        onboard.off()
    gc.collect()
    html = webpage()
    conn.send(html)
    conn.close()