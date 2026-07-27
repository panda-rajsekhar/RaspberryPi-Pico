from machine import Pin
from time import sleep

# ----------------------------------------
# 8-bit Bitwise OR
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


# (A, B) Test Cases
test_cases = [
    (0b11001100, 0b10101010),
    (0b11110000, 0b00001111),
    (0b11111111, 0b01010101),
    (0b00111100, 0b11110000),
    (0b10011001, 0b01100110)
]


while True:

    for A, B in test_cases:

        result = A ^ B

        print("--------------------------------")
        print("         BITWISE XOR (^)")
        print("--------------------------------")

        print(f"A      : {A:08b}")
        write_byte(A)
        sleep(2)

        print(f"B      : {B:08b}")
        write_byte(B)
        sleep(2)

        # Small pause
        write_byte(0)
        sleep(0.5)

        print("----------------")
        print(f"Result : {result:08b}")
        write_byte(result)
        sleep(3)

        # Clear before next example
        write_byte(0)
        sleep(1)
