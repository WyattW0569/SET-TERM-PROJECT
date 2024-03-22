from utime import sleep

def readValueFrom(state):
    return 1


IRSensorValue = readValueFrom(0)
lastSensorValue = IRSensorValue

while True:
    lastSensorValue = IRSensorValue
    IRSensorValue = readValueFrom(0)

    if lastSensorValue-IRSensorValue < 100: #tune this and sleep value to adust sensitivity of motion sensor
        print ("motion detected")

    sleep (0.2)

