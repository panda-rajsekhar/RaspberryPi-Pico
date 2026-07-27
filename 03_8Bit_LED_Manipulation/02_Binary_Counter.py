from machine import Pin
from time import sleep

# ----------------------------------------
# 8-bit LED Binary Counter
# Raspberry Pi Pico (MicroPython)
#
# D7 (MSB) -> GP21 (Blue)
# D6       -> GP20 (Blue)
# D5       -> GP19 (Blue)
# D4       -> GP18 (Blue)
# D3       -> GP17 (Red)
# D2       -> GP16 (Red)
# D1       -> GP15 (Red)
# D0 (LSB) -> GP14 (Red)
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


# Main Loop
while True:
    for number in range(256):
        write_byte(number)
        print(f"Decimal: {number:3d}    Binary: {number:08b}")
        sleep(0.1)

