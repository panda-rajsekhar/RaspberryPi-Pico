"""
PCF8574 I2C backpack backend for an HD44780 character LCD.

Typical PCF8574 backpack mapping used by this driver:
    P0 -> RS
    P1 -> RW
    P2 -> E
    P3 -> Backlight
    P4..P7 -> LCD D4..D7

RW is kept low because the common PCF8574 backpack wiring does not
provide useful LCD-busy reads through this driver.
"""

import time
from lcd_api import LcdApi


class I2cLcd(LcdApi):
    # PCF8574 output bits
    RS = 0x01
    RW = 0x02
    ENABLE = 0x04
    BACKLIGHT = 0x08
    DATA_SHIFT = 4

    def __init__(self, i2c, address, rows=2, cols=16):
        self.i2c = i2c
        self.address = address
        self._backlight = True

        # One reusable 1-byte buffer avoids allocating a new bytes object
        # for every I2C transaction.
        self._tx = bytearray(1)

        # Start with the expander outputs low.
        self._write_expander(0)

        # HD44780 power-up sequence in 4-bit mode.
        time.sleep_ms(30)
        self._init_nibble(0x30)
        time.sleep_ms(5)
        self._init_nibble(0x30)
        time.sleep_ms(1)
        self._init_nibble(0x30)
        time.sleep_ms(1)
        self._init_nibble(0x20)
        time.sleep_ms(1)

        super().__init__(rows, cols)

    # ---------- PCF8574 transport ----------

    def _write_expander(self, value):
        if self._backlight:
            value |= self.BACKLIGHT
        self._tx[0] = value & 0xFF
        self.i2c.writeto(self.address, self._tx)

    def _pulse_enable(self, value):
        self._write_expander(value | self.ENABLE)
        time.sleep_us(1)
        self._write_expander(value & ~self.ENABLE)
        time.sleep_us(1)

    def _send_nibble(self, nibble, rs):
        value = ((nibble & 0x0F) << self.DATA_SHIFT) | rs
        # RW stays low: write-only operation.
        self._pulse_enable(value)

    def _init_nibble(self, command):
        self._send_nibble((command >> 4) & 0x0F, 0)

    def _write_command(self, value):
        self._send_nibble((value >> 4) & 0x0F, 0)
        self._send_nibble(value & 0x0F, 0)

        # CLEAR and HOME are the slow HD44780 commands.
        if value in (self.CMD_CLEAR, self.CMD_HOME):
            time.sleep_ms(2)

    def _write_data(self, value):
        self._send_nibble((value >> 4) & 0x0F, self.RS)
        self._send_nibble(value & 0x0F, self.RS)

    # ---------- Backlight ----------

    def _backlight_on(self):
        self._backlight = True
        self._write_expander(0)

    def _backlight_off(self):
        self._backlight = False
        self._write_expander(0)

