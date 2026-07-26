import time
import board
import digitalio

led_onb = digitalio.DigitalInOut(board.LED)
led_onb.direction = digitalio.Direction.OUTPUT

while True:
    led_onb.value = 1
    time.sleep(.1)
    led_onb.value = 0
    time.sleep(0.1)