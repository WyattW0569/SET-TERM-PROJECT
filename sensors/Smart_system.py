from machine import Pin, PWM

# sets pins 10-12 as PWM pins for the RGB LED
rgbG = PWM (Pin(10))
rgbB = PWM (Pin(11))
rgbR = PWM (Pin(12))

#sets frequency of PWM pins
rgbB.freq(1000)
rgbG.freq(1000)
rgbR.freq(1000)

# this function sets the LED light to the RGB color code it is given in a array
def setColor( colorcode ):
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

    

while True:
    white = [255,255,255]
    teal = [66,254,224]
    orange = [255,255,0]

    setColor(orange)
    