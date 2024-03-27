

from time import sleep
from math import log, trunc
from machine import ADC

extTempSensor = ADC(26)

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

while True:
    Temp = readExtTemperature()
    print(Temp)
    Temp = trunc(Temp)
    print(Temp)
    sleep(0.2)