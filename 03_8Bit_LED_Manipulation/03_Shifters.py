from machine import Pin
from time import sleep

# ----------------------------------------
# 8-bit LED Shifters
# Raspberry Pi Pico (MicroPython)
#
# D7 (MSB) -> GP21
# D6       -> GP20
# D5       -> GP19
# D4       -> GP18
# D3       -> GP17
# D2       -> GP16
# D1       -> GP15
# D0 (LSB) -> GP14
# ----------------------------------------

# GPIO mapping (D7 to D0)
led_pins = [21, 20, 19, 18, 17, 16, 15, 14]
leds = [Pin(pin, Pin.OUT) for pin in led_pins]


def write_byte(value):
    """Display an 8-bit value on the LEDs."""
    value &= 0xFF

    for i in range(8):
        bit = (value >> (7 - i)) & 1
        leds[i].value(bit)


while True:

    print("\nLEFT SHIFT (<<)\n")

    value = 0x01

    while value <= 0x80:
        write_byte(value)
        print(f"{value:08b}")
        sleep(0.4)
        value <<= 1

    sleep(1)

    print("\nRIGHT SHIFT (>>)\n")

    value = 0x80

    while value >= 0x01:
        write_byte(value)
        print(f"{value:08b}")
        sleep(0.4)
        value >>= 1

    sleep(1)

