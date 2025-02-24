import socket
import time
import pigpio
import RPi.GPIO as GPIO

TRIG1 = 2
ECHO1 = 3

TRIG2 = 20
ECHO2 = 21

led_pin = 19


pi = pigpio.pi()
GPIO.setmode(GPIO.BCM)

IN1 = 17
IN2 = 18
ENA = 12
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
pwm_motor1 = GPIO.PWM(ENA, 1000)
pwm_motor1.start(0)

IN3 = 23
IN4 = 22
ENB = 13
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)
pwm_motor2 = GPIO.PWM(ENB, 1000)
pwm_motor2.start(0)

GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, GPIO.LOW)

HOST = '192.168.137.139'
PORT = 12346

def measure_distance(TRIG, ECHO):
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def ledon():
    GPIO.output(led_pin, GPIO.HIGH)

def ledoff():
    GPIO.output(led_pin, GPIO.LOW)

def control(angle):
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180

    duty_cycle = angle*(1000/90) +500
    pi.set_servo_pulsewidth(24, duty_cycle)

def forward(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_motor1.ChangeDutyCycle(speed)
    pwm_motor2.ChangeDutyCycle(speed)

def backward(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_motor1.ChangeDutyCycle(speed)
    pwm_motor2.ChangeDutyCycle(speed)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Waiting for a connection...')
    
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            received_integer = int(data.decode('utf-8'))
            if received_integer<160 and received_integer>40:
                control(received_integer)
                forward(100)

                try:
                    distance1 = measure_distance(2, 3) #전방 센서
                    distance2 = measure_distance(20, 21) #상방 센서

                    if distance1 < 40:
                        control(received_integer)
                        forward(0)
                        time.sleep(2)
                        distance1 = measure_distance(2, 3)
                        distance2 = measure_distance(20, 21)
                        if distance1 < 40:
                            control(90)
                            backward(80)
                            time.sleep(1.2)
                            control(150)
                            forward(80)
                            time.sleep(0.8)
                            control(90) 
                            time.sleep(0.01)
                        else :
                            pass     
                    elif distance2 < 40:
                        control(received_integer) 
                        ledon()
                    elif distance2 >= 40:
                        ledoff()

                    time.sleep(0.1)

                except KeyboardInterrupt:
                    GPIO.cleanup()

GPIO.cleanup()
