from machine import Pin
from time import sleep

red = Pin(12, Pin.OUT)
green = Pin(13, Pin.OUT)
blue = Pin(14, Pin.OUT)
white = Pin(15, Pin.OUT)

while True:
    red.on()
    blue.on()
    green.off()
    white.off()
    sleep(0.4)

    red.off()
    blue.off()
    green.on()
    white.on()
    sleep(0.4)
