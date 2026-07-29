from machine import Pin, I2C

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

devices = i2c.scan()

if devices:
    print("I2C devices found:")
    for device in devices:
        print(hex(device))
else:
    print("No I2C device found.")

