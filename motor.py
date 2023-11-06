import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # Set the GPIO mode to use the BCM numbering
servo_pin = 17           # The GPIO pin connected to the servo
GPIO.setup(servo_pin, GPIO.OUT)

# Create a PWM object with a frequency of 50 Hz
pwm = GPIO.PWM(servo_pin, 50)

# Start the PWM signal with a duty cycle of 0 (servo at 0 degrees)
pwm.start(0)

try:
    while True:
        # Move the servo to a specific angle by changing the duty cycle
        angle = float(input("Enter the angle (0 to 180 degrees): "))
        duty_cycle = 2.5 + 10 * angle / 180  # Map the angle to the duty cycle
        pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()  # Stop the PWM signal
    GPIO.cleanup()  # Clean up the GPIO configuration
