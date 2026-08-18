from machine import I2C, Pin
import time

I2C_ID = 0
SDA_PIN = 0
SCL_PIN = 1
FREQUENCY = 400_000

i2c = I2C(
    I2C_ID,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=FREQUENCY,
)

time.sleep_ms(100)

devices = i2c.scan()

if not devices:
    print("No I2C devices found.")
else:
    print("I2C devices found:")
    for address in devices:
        print("  0x{:02X}".format(address))
