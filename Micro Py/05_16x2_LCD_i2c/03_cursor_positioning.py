from machine import Pin, I2C
from i2c_lcd import I2cLcd

i2c = I2C(
    0,
    sda=Pin(0),
    scl=Pin(1),
    freq=400000
)

lcd = I2cLcd(i2c, 0x27, 2, 16)

lcd.clear()

lcd.move_to(0, 0)
lcd.putstr("Rajsekhar Panda")

lcd.move_to(0, 1)
lcd.putstr("Pico LCD")

