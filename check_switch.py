import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)
gpio.setup(21, gpio.IN, pull_up_down=gpio.PUD_DOWN)
 
while True:
    print(gpio.input(21))
    if gpio.input(21) == 1:     
        print("LOW")
        break


gpio.cleanup()
