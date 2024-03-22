import machine
from time import sleep


redLED_pin = machine.Pin(14, machine.Pin.OUT)
adc = machine.ADC(26) 

while True:
    adc_value = adc.read_u16()
    print(adc_value)

    if adc_value < 2048: # the threshold value must be tuned based on test environment. Ambient light also has IR rays. 
            redLED_pin.on()
    else:
            redLED_pin.off()
    sleep(0.05)
