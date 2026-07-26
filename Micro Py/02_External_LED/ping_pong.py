from machine import Pin
from time import sleep

leds = [
    Pin(12, Pin.OUT),
    Pin(13, Pin.OUT),
    Pin(14, Pin.OUT),
    Pin(15, Pin.OUT)
]

while True:
    for i in range(len(leds)):
        leds[i].on()
        sleep(0.15)
        leds[i].off()

    for i in range(len(leds) - 2, 0, -1):
        leds[i].on()
        sleep(0.15)
        leds[i].off()
