"""
JAI JAGANNATH
=========================================
4x4 Matrix Keypad Driver
=========================================

Author : Rajsekhar Panda

Description:
Reusable 4x4 matrix keypad driver for the
Raspberry Pi Pico.
"""

from machine import Pin
from time import sleep_ms


class Keypad:

    def __init__(
        self,
        row_pins=(6, 7, 8, 9),
        col_pins=(10, 4, 3, 2),      # GPIO10 replaces GPIO5
        debounce=20
    ):

        self.rows = [
            Pin(pin, Pin.IN, Pin.PULL_DOWN)
            for pin in row_pins
        ]

        self.cols = [
            Pin(pin, Pin.OUT)
            for pin in col_pins
        ]

        for col in self.cols:
            col.value(0)

        # -----------------------------------------
        # Logical Key Mapping
        # -----------------------------------------

        self.keys = [
            ['S13', 'S14', 'S15', 'S16'],
            ['S9',  'S10', 'S11', 'S12'],
            ['S5',  'S6',  'S7',  'S8'],
            ['S1',  'S2',  'S3',  'S4']
        ]

        self.debounce = debounce
        self.last_key = None

    # -----------------------------------------
    # Read One Key Press
    # -----------------------------------------

    def get_key(self):

        while True:

            detected = None

            for c in range(4):

                self.cols[c].value(1)

                for r in range(4):

                    if self.rows[r].value():
                        detected = self.keys[r][c]

                self.cols[c].value(0)

            # New key press
            if detected is not None and self.last_key is None:

                self.last_key = detected
                sleep_ms(self.debounce)
                return detected

            # Key released
            elif detected is None:

                self.last_key = None

            sleep_ms(1)
