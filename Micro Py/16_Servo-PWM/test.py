from machine import Pin, PWM
from time import sleep

servo = PWM(Pin(15))
servo.freq(50)


def set_angle(angle):
    # Servo range: 0°–90°
    pulse_us = 1000 + (1000 * angle // 90)

    # 50 Hz = 20 ms = 20,000 µs
    duty = int(pulse_us * 65535 / 20000)

    servo.duty_u16(duty)


while True:
    print("0°")
    set_angle(0)
    sleep(1)

    print("30°")
    set_angle(30)
    sleep(1)

    print("60°")
    set_angle(60)
    sleep(1)

    print("90°")
    set_angle(90)
    sleep(1)