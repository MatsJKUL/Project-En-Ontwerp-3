import pigpio
import RPi.GPIO as GPIO
import time
DEBUG = False

GPIO.setmode(GPIO.BCM) #setup motors
servo1_pin = 15
servo2_pin = 14
dc1_pin = 17
dc2_pin = 18
switch_pin = 27

pwm1 = pigpio.pi(port=30000)

current_pos_2 = 0

def turn_servo2(angle):
    global current_pos_2
    print('turnservo2')

    if angle > current_pos_2:
        print("FORWARD")
        for i in range(int(current_pos_2), int(angle) + 1):
            pulsewidth =  int(2000*i/270 + 500) # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo2_pin, pulsewidth)
            time.sleep(0.01)

    elif angle < current_pos_2:
        print("BACK")
        for i in range(int(current_pos_2), int(angle) + 1, -1):
            pulsewidth =  int(2000*i/270 + 500) # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo2_pin, pulsewidth)
            time.sleep(0.01)
    current_pos_2 = angle


def test_pulse(pulsewidth):
    angle = int(input("where angle:\n"))
    turn_servo2(angle)

try:
    while True:
        angle = int(input("enter an angle"))
        turn_servo2(angle)
except KeyboardInterrupt:
    pwm1.set_PWM_dutycycle(servo1_pin, 0)
    pwm1.set_PWM_dutycycle(servo2_pin, 0)
    pwm1.set_PWM_frequency(servo1_pin, 0)
    pwm1.set_PWM_frequency(servo2_pin, 0)
    pwm1.stop()
