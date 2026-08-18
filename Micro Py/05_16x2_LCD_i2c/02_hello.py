from machine import I2C, Pin
from i2c_lcd import I2cLcd

I2C_ID = 0
SDA_PIN = 0
SCL_PIN = 1
I2C_ADDRESS = 0x27

i2c = I2C(
    I2C_ID,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=400_000,
)

lcd = I2cLcd(i2c, I2C_ADDRESS, rows=2, cols=16)
lcd.putstr("Hello World!")
