import pigpio
import RPi.GPIO as GPIO
import time

DEBUG = False

####################    MOTOR AND LIMIT_SWITCH   ##########################
GPIO.setmode(GPIO.BCM) #setup motors
servo1_pin = 14
servo2_pin = 15
dc1_pin = 17
dc2_pin = 18
switch_pin = 27
switched = 0

current_pos_1 = 0
current_pos_2 = 0

pwm1 = pigpio.pi(port=30000)

pwm1.set_mode(servo1_pin, pigpio.OUTPUT)
pwm1.set_mode(servo2_pin, pigpio.OUTPUT)

pwm1.set_PWM_frequency(servo1_pin, 50)
pwm1.set_PWM_frequency(servo2_pin, 50)

GPIO.setup(dc1_pin, GPIO.OUT)
GPIO.setup(dc2_pin, GPIO.OUT)
GPIO.setup(switch_pin, GPIO.OUT)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #setup limit_switch
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setmode(GPIO.BCM)  # Set the GPIO mode to use the BCM numbering
print("init pins")

def turn_dc1():
    print('turndc1')
    GPIO.output(dc1_pin, GPIO.HIGH)

def stop_dc1():
    GPIO.output(dc1_pin, GPIO.LOW)

def turn_dc2():
    print('dc2')
    GPIO.output(dc2_pin, GPIO.HIGH)
    print("turned")

def switch_dc2():
    global switched 
    print("switch")
    if switched == 0:
        print("FOUR")
        GPIO.output(switch_pin, GPIO.HIGH)
        switched = 1
    elif switched == 1:
        print("ZERO")
        GPIO.output(switch_pin, GPIO.LOW)
        switched = 0


def stop_dc2():
    GPIO.output(dc2_pin, GPIO.LOW)

def turn_servo2(angle):
    global current_pos_2
    print('turnservo2')

    if angle > current_pos_2:
        print("FORWARD")
        for i in range(int(current_pos_2), int(angle) + 1):
            pulsewidth =  2000*i/270 + 500 # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo2_pin, pulsewidth)
            time.sleep(.01)

    elif angle < current_pos_2:
        print("BACK")
        for i in range(int(current_pos_2), int(angle) + 1, -1):
            pulsewidth =  2000*i/270 + 500 # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo2_pin, pulsewidth)
            time.sleep(.01)
    current_pos_2 = angle

def turn_servo1(angle):
    global current_pos_1
    print('turnservo1')
    if angle > current_pos_1:
        print("FORWARD")
        for i in range(int(current_pos_1), int(angle) + 1):
            pulsewidth =  2000*i/270 + 500 # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo1_pin, pulsewidth)
            time.sleep(.01)

    elif angle < current_pos_1:
        print("BACK")
        for i in range(int(current_pos_1), int(angle) + 1, -1):
            pulsewidth =  2000*i/270 + 500 # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo1_pin, pulsewidth)
            time.sleep(.01)

    current_pos_1 = angle

def servo_stop():
    pwm1.set_PWM_dutycycle(servo1_pin, 0)
    pwm1.set_PWM_dutycycle(servo2_pin, 0)
    pwm1.set_PWM_frequency(servo1_pin, 0)
    pwm1.set_PWM_frequency(servo2_pin, 0)

def shoot_card():
    global switched
    switched = 0
    turn_dc2()
    turn_dc1()
    time.sleep(.275)
    stop_dc2()
    switch_dc2()
    time.sleep(0.2)
    turn_dc2()
    stop_dc1()
    time.sleep(1)
    time.sleep(0.5)
    stop_dc2()
    time.sleep(0.1)
    switch_dc2()
