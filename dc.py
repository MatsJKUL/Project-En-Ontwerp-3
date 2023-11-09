import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin (17) as an output
GPIO.setup(17, GPIO.OUT)

try:
    # Turn the LED on
    GPIO.output(17, GPIO.HIGH)
    print("LED is on")

    # Wait for a few seconds
    time.sleep(3)

    # Turn the LED off
    GPIO.output(17, GPIO.LOW)
    print("LED is off")

except KeyboardInterrupt:
    GPIO.cleanup()  # Cleanup GPIO settings on exit
