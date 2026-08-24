from machine import Pin, PWM
from time import sleep

servo = PWM(Pin(15))
servo.freq(50)


def set_pulse(us):
    duty = int(us * 65535 / 20000)
    servo.duty_u16(duty)


while True:
    print("MIN")
    set_pulse(1000)
    sleep(2)

    print("CENTER")
    set_pulse(1500)
    sleep(2)

    print("MAX")
    set_pulse(2000)
    sleep(2)