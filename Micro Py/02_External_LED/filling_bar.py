from machine import Pin
from time import sleep

leds = [
    Pin(12, Pin.OUT),
    Pin(13, Pin.OUT),
    Pin(14, Pin.OUT),
    Pin(15, Pin.OUT)
]

while True:
    # Fill
    for i in range(4):
        leds[i].on()
        sleep(0.2)

    sleep(0.4)

    # Empty
    for i in range(3, -1, -1):
        leds[i].off()
        sleep(0.2)

    sleep(0.4)
