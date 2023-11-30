import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)
gpio.setup(20, gpio.IN, pull_up_down=gpio.PUD_DOWN)
 
while True:
    print(gpio.input(20))
    if gpio.input(20) == 1:     
        print("LOW")
        break


gpio.cleanup()
