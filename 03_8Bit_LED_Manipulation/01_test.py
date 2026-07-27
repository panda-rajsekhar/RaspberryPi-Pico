from machine import Pin
from time import sleep

# D7 -> D0
leds = [
    Pin(14, Pin.OUT),  # D7
    Pin(15, Pin.OUT),  # D6
    Pin(16, Pin.OUT),  # D5
    Pin(17, Pin.OUT),  # D4
    Pin(18, Pin.OUT),  # D3
    Pin(19, Pin.OUT),  # D2
    Pin(20, Pin.OUT),  # D1
    Pin(21, Pin.OUT)   # D0
]

while True:
    # Turn ON one LED at a time
    for led in leds:
        led.on()
        sleep(0.3)
        led.off()

    sleep(0.5)
    # Turn ON all LEDs
    for led in leds:
        led.on()
    sleep(1)

    # Turn OFF all LEDs
    for led in leds:
        led.off()
    sleep(1)

