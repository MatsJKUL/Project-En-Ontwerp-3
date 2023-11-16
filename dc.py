import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin (pin) as an output
pin = 14 
GPIO.setup(pin, GPIO.OUT)

# Turn the LED on
GPIO.output(pin, GPIO.HIGH)
print("LED is on")

# Wait for a few seconds
time.sleep(2)

# Turn the LED off
GPIO.output(pin, GPIO.LOW)
print("LED is off")

GPIO.cleanup()  # Cleanup GPIO settings on exit
