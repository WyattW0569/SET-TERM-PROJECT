import machine
from time import sleep
from math import log



temp_sensor = machine.ADC(27)
conversion_factor = 3.3 / 65535 #converts ADC value to voltage between 0 and 3.3 V


while True:
    reading = temp_sensor.read_u16()
    R= (3.3*10000)/(reading*conversion_factor)-10000 #calculates the resistance of the thermistor
    a=1.4 * pow(10, -3) #varibles for the stienhart-Hart equation
    b=2.37 * pow(10,-4) #varibles for the stienhart-Hart equation
    c=9.9 * pow(10, -8) #varibles for the stienhart-Hart equation
    Temperature = 1/(a + (b * log(R) ) + c * pow(( log(R)), 3) ) #the stienhart-Hart equation. calculates temperature read from resistance value
    Temperature = Temperature - 241.83 #adustment from absolute temperature to celcius- tuned slightly based on individual thermistor
    print(Temperature)
    sleep(1)