from machine import Pin, I2C
from i2c_lcd import I2cLcd
import time

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

lcd.putstr("Hello World!")
time.sleep(2)

lcd.home()
lcd.putstr("Panda")

