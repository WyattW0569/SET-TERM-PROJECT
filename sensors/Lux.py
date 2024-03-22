import machine
from time import sleep


while True:
    max_read = 65535  #The maximum value of the ADC pins 
    raw_data = machine.ADC(27)  #Read the raw input from the ADC pin
    data = raw_data.read_u16()  #Take the value out of the raw_data

    resistor_voltage = data / (max_read * 3.3)  #Converting the data read into a voltage voltage of the resistor
    photo_voltage = 3.3 - resistor_voltage  #Calculating the voltage of the photo_resistor
    photo_resistance = photo_voltage/resistor_voltage*3.3  #Calculating the resistance of the photo resistor

    Lux = pow(photo_resistance,-1.4059)(12518931)  #Calculate the Lux(Unit of light) that the photoresistor is sensing
    print("Lux",Lux)  #Print the value to view current light level in terminal
    sleep(0.1)  