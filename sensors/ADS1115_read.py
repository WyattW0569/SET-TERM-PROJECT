from utime import sleep
from machine import I2C, Pin, ADC


dev = I2C (1, scl=Pin(15), sda=Pin(14)) # configure pico to recoignise pins 14 and 15 as scl and sda pins for an external device


# device recognition and adress for ADS1115
devices = dev.scan() # find where device is 
for device in devices:  # print device adress (72)
    print(device) # was used to find address of ADS 1115
address = 72 # put adress in varibe address


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



#test using IR sensor

redLED_pin = Pin(16, Pin.OUT)

IRSensorValue = readValueFrom(0)
lastSensorValue = IRSensorValue

while True:
    lastSensorValue = IRSensorValue
    IRSensorValue = readValueFrom(0)
    difference = abs(IRSensorValue - lastSensorValue)

    print (IRSensorValue)
    print (lastSensorValue)
    print (difference)

    if difference > 25: #tune this and sleep value to adust sensitivity of motion sensor
        redLED_pin.on()
    else:
        redLED_pin.off()

    sleep (0.1)


