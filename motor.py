import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # Set the GPIO mode to use the BCM numbering
servo_pin = 14          # The GPIO pin connected to the servo
GPIO.setup(servo_pin, GPIO.OUT)
current_pos = 0

# Create a PWM object with a frequency of 50 Hz
pwm = GPIO.PWM(servo_pin, 50)

# Start the PWM signal with a duty cycle of 0 (servo at 0 degrees)
pwm.start(0)

duty_cycle = 2.5 + 10 * 0 / 270  # Map the angle to the duty cycle
pwm.ChangeDutyCycle(duty_cycle)

try:
    while True:
        # Move the servo to a specific angle by changing the duty cycle
        angle = float(input("Enter the angle (0 to 180 degrees): "))

        if angle > current_pos:
            print("FORWARD")
            for i in range(int(current_pos), int(angle) + 1):
                duty_cycle = 2.5 + 10 * i / 270  # Map the angle to the duty cycle
                pwm.ChangeDutyCycle(duty_cycle)
                time.sleep(.01)

        elif angle < current_pos:
            print("BACK")
            for i in range(int(current_pos), int(angle) + 1, -1):
                duty_cycle = 2.5 + 10 * i / 270  # Map the angle to the duty cycle
                pwm.ChangeDutyCycle(duty_cycle)
                time.sleep(.01)
        current_pos = angle

except KeyboardInterrupt:
    pwm.stop()  # Stop the PWM signal
    GPIO.cleanup()  # Clean up the GPIO configuration
