from machine import Pin, I2C
from i2c_lcd import I2cLcd

# ----------------------------
# Initialize LCD
# ----------------------------
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# ----------------------------
# Custom Characters
# ----------------------------

# Slot 0 - Heart
heart = [
    0b01010,
    0b11111,
    0b11111,
    0b11111,
    0b01110,
    0b00100,
    0b00000,
    0b00000,
]

# Slot 1 - Smiley
smiley = [
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b10001,
    0b01110,
    0b00000,
    0b00000,
]

# Slot 2 - Tick
tick = [
    0b00000,
    0b00001,
    0b00010,
    0b10100,
    0b01000,
    0b00000,
    0b00000,
    0b00000,
]

# Slot 3 - Cross
cross = [
    0b10001,
    0b01010,
    0b00100,
    0b01010,
    0b10001,
    0b00000,
    0b00000,
    0b00000,
]

# Slot 4 - Up Arrow
up = [
    0b00100,
    0b01110,
    0b10101,
    0b00100,
    0b00100,
    0b00100,
    0b00000,
    0b00000,
]

# Slot 5 - Down Arrow
down = [
    0b00100,
    0b00100,
    0b00100,
    0b10101,
    0b01110,
    0b00100,
    0b00000,
    0b00000,
]

# Slot 6 - Wi-Fi
wifi = [
    0b00000,
    0b01110,
    0b10001,
    0b00100,
    0b01010,
    0b00000,
    0b00100,
    0b00000,
]

# Slot 7 - Battery
battery = [
    0b01110,
    0b11011,
    0b11011,
    0b11011,
    0b11011,
    0b11011,
    0b11111,
    0b00000,
]

# ----------------------------
# Load into CGRAM
# ----------------------------

lcd.custom_char(0, heart)
lcd.custom_char(1, smiley)
lcd.custom_char(2, tick)
lcd.custom_char(3, cross)
lcd.custom_char(4, up)
lcd.custom_char(5, down)
lcd.custom_char(6, wifi)
lcd.custom_char(7, battery)

# ----------------------------
# Display
# ----------------------------

lcd.clear()

lcd.putchar(chr(0))
lcd.putchar(" ")

lcd.putchar(chr(1))
lcd.putchar(" ")

lcd.putchar(chr(2))
lcd.putchar(" ")

lcd.putchar(chr(3))

lcd.move_to(0, 1)

lcd.putchar(chr(4))
lcd.putchar(" ")

lcd.putchar(chr(5))
lcd.putchar(" ")

lcd.putchar(chr(6))
lcd.putchar(" ")

lcd.putchar(chr(7))
