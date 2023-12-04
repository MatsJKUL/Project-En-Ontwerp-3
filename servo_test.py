import pigpio
import RPi.GPIO as GPIO
import time
DEBUG = False

GPIO.setmode(GPIO.BCM) #setup motors
servo1_pin = 14
servo2_pin = 15
dc1_pin = 17
dc2_pin = 18
switch_pin = 27

pwm1 = pigpio.pi()
pwm2 = pigpio.pi()

pwm1.set_mode(servo1_pin, pigpio.OUTPUT)
pwm2.set_mode(servo2_pin, pigpio.OUTPUT)

pwm1.set_PWM_frequency(servo1_pin, 50)
pwm2.set_PWM_frequency(servo2_pin, 50)
current_pos_2 = 0

def turn_servo2(angle, current_pos_2):
    print('turnservo2')

    if angle > current_pos_2:
        print("FORWARD")
        for i in range(int(current_pos_2), int(angle) + 1):
            pulsewidth = i/90*1000 + 500 # Map the angle to the duty cycle
            pwm2.set_servo_pulsewidth(servo2_pin, pulsewidth)
            time.sleep(.01)

    elif angle < current_pos_2:
        print("BACK")
        for i in range(int(current_pos_2), int(angle) + 1, -1):
            pulsewidth = i/90*1000 + 500 # Map the angle to the duty cycle
            pwm2.set_servo_pulsewidth(servo2_pin, pulsewidth)
            time.sleep(.01)

    current_pos_2 = angle
    return current_pos_2

try:
    while True:
        angle = int(input("enter an angle"))
        current_pos_2 = turn_servo2(angle, current_pos_2)
except KeyboardInterrupt:
    pwm1.set_PWM_dutycycle(servo1_pin, 0)
    pwm2.set_PWM_dutycycle(servo2_pin, 0)
    pwm1.set_PWM_frequency(servo1_pin, 0)
    pwm2.set_PWM_frequency(servo2_pin, 0)