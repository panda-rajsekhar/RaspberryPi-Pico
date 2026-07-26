from machine import Pin
from time import sleep

leds = [
    Pin(12, Pin.OUT),
    Pin(13, Pin.OUT),
    Pin(14, Pin.OUT),
    Pin(15, Pin.OUT)
]

while True:
    for led in leds:
        led.on()
        sleep(0.2)
        led.off()
