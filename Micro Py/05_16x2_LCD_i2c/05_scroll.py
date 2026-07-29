from machine import Pin, I2C
from i2c_lcd import I2cLcd
import time

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

lcd.putstr("Raspberry PiPico")

time.sleep(2)

#scrolls left and rigt the string 

while True:
    for _ in range(16):
        lcd.scroll_left()
        time.sleep(0.2)

    for _ in range(16):
        lcd.scroll_right()
        time.sleep(0.2)

