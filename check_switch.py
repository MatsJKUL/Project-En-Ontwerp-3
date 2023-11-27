import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)
gpio.setup(21, gpio.IN, pull_up_down=GPIO.PUD_UP)
 
while True
    if gpio.input(21) == 0:     
        print("LOW")
        break


gpio.cleanup()
