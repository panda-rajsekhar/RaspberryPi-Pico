from machine import Pin
from time import sleep

# Push Button (Internal Pull-Up)
button = Pin(15, Pin.IN, Pin.PULL_UP)

# Raspberry Pi Pico Onboard LED
led = Pin("LED", Pin.OUT)

while True:

    if button.value() == 0:
        led.on()          # Button Pressed

    else:
        led.off()         # Button Released

    sleep(0.01)
