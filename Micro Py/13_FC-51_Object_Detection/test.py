from machine import Pin, I2C
from i2c_lcd import I2cLcd
from time import sleep

# ---------------- LCD ----------------
i2c = I2C(
    0,
    sda=Pin(0),
    scl=Pin(1),
    freq=400000
)

lcd = I2cLcd(i2c, 0x27, 2, 16)

# ---------------- FC-51 ----------------
sensor = Pin(2, Pin.IN)

# ---------------- Main Program ----------------
lcd.clear()
lcd.putstr("Proximity Sensor")
sleep(2)

while True:

    if sensor.value() == 0:
        # Object detected
        lcd.clear()
        lcd.putstr("OBJECT DETECTED")
        lcd.move_to(0, 1)
        lcd.putstr("Nearby!")
    else:
        # No object
        lcd.clear()
        lcd.putstr("NO OBJECT")
        lcd.move_to(0, 1)
        lcd.putstr("Detected")

    sleep(0.2)