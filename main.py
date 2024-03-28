import network
import socket
from time import sleep
import machine
from machine import I2C, Pin, ADC, PWM
from math import log, trunc
import _thread
import gc


#VARIABLES
dev = I2C (1, scl=Pin(15), sda=Pin(14)) # configure pico to recoignise pins 14 and 15 as scl and sda pins for an external device (ADC Expansion board)

# sets pins 10-12 as PWM (pulse width modulation) pins for the RGB LED.
rgbG = PWM (Pin(10))
rgbB = PWM (Pin(11))
rgbR = PWM (Pin(12))

#sets frequency of PWM pins
rgbB.freq(1000)
rgbG.freq(1000)
rgbR.freq(1000)

# sets pins for temp sensors
intTempSensor = ADC(26)
extTempSensor = ADC(27)

# sets pins for HVAC actuators
heatON = Pin(17, Pin.OUT)
coolON = Pin(16, Pin.OUT)


#defines ports of light sensors
intLightSensor = 1
extLightSensor = 2
turnLightOn = False
global lightState 
lightState = False



# RGB values for setRGB function
rgbOn = [255,255,255]
rgbWarm = [255,200,100]
rgbCool = [100,200,255]
rgbOff = [0,0,0]
rgbCurrent = rgbOn

#WEB IMPL
onboard = Pin("LED", Pin.OUT, value=0)
minTemp = 24
maxTemp = 28
curTemp = 0
outTemp = 0
curLightMode = "default"



# device recognition and adress for ADS1115
devices = dev.scan() # find where device is 
for device in devices:  # print device adress (72)
    print(device) # was used to find address of ADS 1115
address = 72 # put adress in varibe address


#Network Setup
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



#FUNCTIONS

#ADS1115_read functions
# this function reads the configuration of the ADS1115 ADC expansion board
def readConfig(): # reads config of ADS1115
    dev.writeto(address, bytearray([1])) # Writing to register 1 (config)
    result = dev.readfrom(address, 2) # specify 2 bytes

    return result[0]<<8 | result[0] # returns current config

# this function reads values from the ADS1115 ADC expansion board
def readValueFrom(port): # reads adc value from ADS1115 ports 0-3

    config = readConfig() # calls readConfig function and writes to varible

    config &= ~(7<<12) # clear MUX bits 
    config &= ~(7<<9) # clear Programmable Gain Amplifier (PGA)

    config |= (7 & (4+port)) << 12 # tells what port to read
    config |= (1<<15) # trigger next conversion
    config |= (1<<9) # set gain to 4.096 volts

    config = [ int(config>>i & 0xff) for i  in [8,0]] #convert config to an array

    dev.writeto(address, bytearray([1] + config)) # write back to ADS1115 as string

    config = readConfig() # monitor bit 15 until it = 1
    while (config & 0x8000) == 0: #loop until bit 15 = 1
        config = readConfig()

    dev.writeto(address, bytearray([0])) # write to register 0 to specify that we are reading the value
    result = dev.readfrom(address, 2) # read 2 bytes

    return result[0]<<8 | result[1] # return value 

#LED functions
# this function sets the LED light to the RGB color code it is given in a array
def setRGBColor( colorcode ):
    #read RGB values into varibles
    rVal = colorcode[0] 
    gVal = colorcode[1] 
    bVal = colorcode[2]
    #adust for PWM input value (0-65535)
    rVal=rVal*257
    gVal=gVal*257
    bVal=bVal*257
    #set pins to value
    rgbR.duty_u16(rVal)
    rgbG.duty_u16(gVal)
    rgbB.duty_u16(bVal)

#IR functions
# this function is to detect motion from the IR sensor
def IRmotion(lastIRValue):
    IRValue = readValueFrom(0) #reads new IR Sensor value
    difference = abs(IRValue-lastIRValue) #compares current and last sensor value
    #print (IRValue, lastIRValue, difference)
    if difference>25: #tune the > value to adust sensitivity
        return True, IRValue # if > threashold: motion detected. return True for motion and current IR value to be sent next function call
    else:
        return False, IRValue # same as true but with false
    
#Thermistor functions
# as thermistors are all slightly different, having one functions for each lets the values be tuned more finely and therfore achive a better reading
# this function reads the temperature read by the interior thermistor 
def readIntTemperature():
    conversion_factor = 3.3 / 65535
    reading = intTempSensor.read_u16()
    Resistance = (3.3*10000)/(reading*conversion_factor)-10000 #calculates the resistance of the thermistor
    a=1.4 * pow(10, -3) #varibles for the stienhart-Hart equation
    b=2.37 * pow(10,-4) #varibles for the stienhart-Hart equation
    c=9.9 * pow(10, -8) #varibles for the stienhart-Hart equation
    Temperature = 1/(a + (b * log(Resistance) ) + c * pow(( log(Resistance)), 3) ) #the stienhart-Hart equation. calculates temperature read from resistance value
    Temperature = Temperature - 241.83 #adustment from absolute temperature to celcius- tuned slightly based on individual thermistor
    Temperature = Temperature*10
    Temperature = trunc(Temperature)
    Temperature = Temperature/10
    return Temperature

# this function reads the temperature read by the exterior thermistor
def readExtTemperature():
    conversion_factor = 3.3 / 65535
    reading = extTempSensor.read_u16()
    Resistance = (3.3*10000)/(reading*conversion_factor)-10000 #calculates the resistance of the thermistor
    a=1.4 * pow(10, -3) #varibles for the stienhart-Hart equation
    b=2.37 * pow(10,-4) #varibles for the stienhart-Hart equation
    c=9.9 * pow(10, -8) #varibles for the stienhart-Hart equation
    Temperature = 1/(a + (b * log(Resistance) ) + c * pow(( log(Resistance)), 3) ) #the stienhart-Hart equation. calculates temperature read from resistance value
    Temperature = Temperature - 241.83 #adustment from absolute temperature to celcius- tuned slightly based on individual thermistor
    Temperature = Temperature*10
    Temperature = trunc(Temperature)
    Temperature = Temperature/10
    return Temperature

#function for calculating if a room is bright enough without the light on
def readLight(port):
    maxread=26000
    maxvoltage= 3.3
    voltage=readValueFrom(port)
    voltage= voltage/maxread*maxvoltage
    if voltage>2.55:
        return True
    else:
        return False
    
            
            # decide to turn lights on based on current values
def lightOn():        
    intLight = readLight(intLightSensor)
    extLight = readLight(extLightSensor)

    if extLight and not intLight:
        print('open blinds you idiot')
        return False
    elif intLight and extLight and not lightState:
        print('no')
        return False
    else:
        print('yes')
        return True

#Web functions
def get_html(html_name,css_name):
   with open(html_name, 'r') as file:
      html = file.read().format(Current_temp=curTemp,MIN=minTemp,MAX=maxTemp,outdoor_temp=outTemp,light_mode=curLightMode)
      file.close()
   with open(css_name, 'r') as file1:
      css = file1.read()
      file1.close()
   input_file = str(html)+"<style>" +str(css)+ "</style>"
   return input_file

def webpage():
    html = get_html('index.html','styles.css')
    return str(html)

#Sensor main loop
motion = [False,readValueFrom(0)]
def sensor_main(motion,lightCount):
    while True:
        motion = IRmotion(motion[1]) # call IR motion function with the last value of sensor readout

        # sets current color based on temperature values
        if(readExtTemperature()>(maxTemp+minTemp)/2):
            rgbCurrent=rgbCool
        elif(readExtTemperature()<(maxTemp+minTemp)/2):
            rgbCurrent=rgbWarm
        else:
            rgbCurrent=rgbOn

        turnLightOn=lightOn()
        print(turnLightOn)
        # If elif turns on or off lights based on motion and delay
        if motion[0] and turnLightOn:
            setRGBColor(rgbCurrent) # calls setRGB function to turn on LED
            lightState = True
            lightCount = 0
        elif lightCount>20:
            setRGBColor(rgbOff) # calls setRGB function to turn off LED\
            lightState = False
            lightCount = 0
        lightCount +=1 

        if (readIntTemperature() < minTemp):
            heatON.on()
        else:
            heatON.off()
                
        if (readIntTemperature() > maxTemp):
            coolON.on()
        else:
            coolON.off()


        sleep (0.1)
_thread.start_new_thread(sensor_main,(motion,0))


#MAIN LOOP
while True:
    #Web Var Stuff
    curTemp = readIntTemperature()

    #Webpage stuff
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)
    try:
        request = request.split()[1]
    except IndexError:
        pass
    if request == '/mintempup?':
        minTemp+=1
    if request == '/mintempdown?':
        minTemp-=1
    if request == '/maxtempup?':
        maxTemp+=1
    if request == '/maxtempdown?':
        maxTemp-=1
    elif request == '/lightoff?':
        onboard.off()
    sleep(2)
    request='/?'
    html = webpage()
    conn.send(html)
    conn.close()