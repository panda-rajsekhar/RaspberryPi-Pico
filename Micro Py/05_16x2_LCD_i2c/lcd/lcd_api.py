"""
HD44780 character LCD command layer.

This module contains the LCD-controller logic only.  It does not know
how bytes reach the display; a hardware backend implements the two
low-level write methods.

Designed for MicroPython and intended for HD44780-compatible 16x2/20x4
character displays.
"""

import time


class LcdApi:
    # HD44780 instruction set
    CMD_CLEAR = 0x01
    CMD_HOME = 0x02

    CMD_ENTRY_MODE = 0x04
    ENTRY_INCREMENT = 0x02
    ENTRY_SHIFT = 0x01

    CMD_DISPLAY = 0x08
    DISPLAY_ON = 0x04
    CURSOR_ON = 0x02
    CURSOR_BLINK = 0x01

    CMD_SHIFT = 0x10
    SHIFT_DISPLAY = 0x08
    SHIFT_RIGHT = 0x04

    CMD_FUNCTION = 0x20
    FUNCTION_8BIT = 0x10
    FUNCTION_2LINE = 0x08
    FUNCTION_5X10 = 0x04

    CMD_CGRAM = 0x40
    CMD_DDRAM = 0x80

    def __init__(self, rows, cols):
        if rows < 1 or rows > 4:
            raise ValueError("rows must be between 1 and 4")
        if cols < 1 or cols > 40:
            raise ValueError("cols must be between 1 and 40")

        self.rows = rows
        self.cols = cols
        self.cursor_col = 0
        self.cursor_row = 0
        self._backlight = True

        # Basic power-up state.
        self.display_off()
        self.backlight_on()
        self.clear()
        self._write_command(self.CMD_ENTRY_MODE | self.ENTRY_INCREMENT)
        self.cursor_off()
        self.display_on()

    # ---------- Public display controls ----------

    def clear(self):
        self._write_command(self.CMD_CLEAR)
        self._delay_ms(2)
        self.cursor_col = 0
        self.cursor_row = 0

    def home(self):
        self._write_command(self.CMD_HOME)
        self._delay_ms(2)
        self.cursor_col = 0
        self.cursor_row = 0

    def display_on(self):
        self._write_command(self.CMD_DISPLAY | self.DISPLAY_ON)

    def display_off(self):
        self._write_command(self.CMD_DISPLAY)

    def cursor_on(self):
        self._write_command(
            self.CMD_DISPLAY | self.DISPLAY_ON | self.CURSOR_ON
        )

    def cursor_off(self):
        self._write_command(
            self.CMD_DISPLAY | self.DISPLAY_ON
        )

    def blink_cursor_on(self):
        self._write_command(
            self.CMD_DISPLAY
            | self.DISPLAY_ON
            | self.CURSOR_ON
            | self.CURSOR_BLINK
        )

    def blink_cursor_off(self):
        self._write_command(
            self.CMD_DISPLAY
            | self.DISPLAY_ON
            | self.CURSOR_ON
        )

    def backlight_on(self):
        self._backlight = True
        self._backlight_on()

    def backlight_off(self):
        self._backlight = False
        self._backlight_off()

    # Compatibility aliases used by some earlier experiments.
    show_cursor = cursor_on
    hide_cursor = cursor_off

    # ---------- Cursor / text ----------

    def move_to(self, col, row):
        if not (0 <= col < self.cols):
            raise ValueError("column outside display")
        if not (0 <= row < self.rows):
            raise ValueError("row outside display")

        # Standard HD44780 row addressing:
        # row 0 = 0x00, row 1 = 0x40, row 2 = 0x00 + cols,
        # row 3 = 0x40 + cols.
        address = col
        if row & 1:
            address += 0x40
        if row & 2:
            address += self.cols

        self._write_command(self.CMD_DDRAM | address)
        self.cursor_col = col
        self.cursor_row = row

    def putchar(self, char):
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("putchar expects one character")

        if char == "\n":
            self.cursor_col = 0
            self.cursor_row = (self.cursor_row + 1) % self.rows
            self.move_to(self.cursor_col, self.cursor_row)
            return

        self._write_data(ord(char))
        self.cursor_col += 1

        if self.cursor_col >= self.cols:
            self.cursor_col = 0
            self.cursor_row = (self.cursor_row + 1) % self.rows

        self.move_to(self.cursor_col, self.cursor_row)

    def putstr(self, text):
        for char in text:
            self.putchar(char)

    # ---------- CGRAM ----------

    def custom_char(self, slot, bitmap):
        if not 0 <= slot <= 7:
            raise ValueError("custom character slot must be 0..7")
        if len(bitmap) != 8:
            raise ValueError("custom character needs exactly 8 rows")

        for row in bitmap:
            if not 0 <= row <= 0x1F:
                raise ValueError("each custom-character row must be 0..31")

        saved_col = self.cursor_col
        saved_row = self.cursor_row

        self._write_command(self.CMD_CGRAM | (slot << 3))
        for row in bitmap:
            self._write_data(row)
            self._delay_us(40)

        self.move_to(saved_col, saved_row)

    # ---------- Display shifting ----------

    def scroll_left(self):
        self._write_command(self.CMD_SHIFT | self.SHIFT_DISPLAY)

    def scroll_right(self):
        self._write_command(
            self.CMD_SHIFT | self.SHIFT_DISPLAY | self.SHIFT_RIGHT
        )

    # ---------- Backend hooks ----------

    def _write_command(self, value):
        raise NotImplementedError

    def _write_data(self, value):
        raise NotImplementedError

    def _backlight_on(self):
        pass

    def _backlight_off(self):
        pass

    @staticmethod
    def _delay_ms(milliseconds):
        time.sleep_ms(milliseconds)

    @staticmethod
    def _delay_us(microseconds):
        time.sleep_us(microseconds)

