from machine import Pin
from time import sleep

led = Pin(25, Pin.OUT)

while True:
    led.toggle()      # Toggle LED state
    sleep(0.5)        # Wait 500 ms