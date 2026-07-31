from machine import Pin, SPI
from time import sleep_ms
from colors import *

# -------------------------------------------------
# Display Configuration
# -------------------------------------------------

WIDTH = 128
HEIGHT = 160

# -------------------------------------------------
# Pixel Formats
# -------------------------------------------------

RGB444 = 0x03
RGB565 = 0x05
RGB666 = 0x06


# -------------------------------------------------
# ST7735 Command Definitions
# -------------------------------------------------

SWRESET = 0x01      # Software Reset
SLPOUT  = 0x11      # Exit Sleep Mode
DISPON  = 0x29      # Display ON

CASET   = 0x2A      # Column Address Set
RASET   = 0x2B      # Row Address Set
RAMWR   = 0x2C      # Memory Write

MADCTL  = 0x36      # Memory Access Control
COLMOD  = 0x3A      # Interface Pixel Format


class ST7735:

    def __init__(
        self,
        spi_id=0,
        baudrate = 40_000_000,
        sck=18,
        mosi=19,
        cs=17,
        dc=21,
        rst=20
    ):

        self.spi = SPI(
            spi_id,
            baudrate=baudrate,
            polarity=0,
            phase=0,
            sck=Pin(sck),
            mosi=Pin(mosi)
        )

        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)

        self.cs.high()
        self.dc.high()
        self.rst.high()

        self.init_display()

    # -------------------------------------------------
    # Hardware Reset
    # -------------------------------------------------

    def hardware_reset(self):

        self.rst.high()
        sleep_ms(5)

        self.rst.low()
        sleep_ms(20)

        self.rst.high()
        sleep_ms(150)

    # -------------------------------------------------
    # Send Command
    # -------------------------------------------------

    def write_cmd(self, cmd):

        self.cs.low()
        self.dc.low()

        self.spi.write(bytearray([cmd]))

        self.cs.high()

    # -------------------------------------------------
    # Send Data
    # -------------------------------------------------

    def write_data(self, data):

        self.cs.low()
        self.dc.high()

        self.spi.write(bytearray([data]))

        self.cs.high()

    # -------------------------------------------------
    # Write 16-bit Value
    # -------------------------------------------------

    def write_u16(self, value):
        self.write_data((value >> 8) & 0xFF)
        self.write_data(value & 0xFF)

    # -------------------------------------------------
    # Display Initialization
    # -------------------------------------------------

    def init_display(self):

        self.hardware_reset()

        self.write_cmd(SWRESET)
        sleep_ms(150)

        self.write_cmd(SLPOUT)
        sleep_ms(150)

        self.write_cmd(COLMOD)
        self.write_data(RGB565)

        self.write_cmd(MADCTL)
        self.write_data(0x00)

        self.write_cmd(DISPON)
        sleep_ms(100)

    # -------------------------------------------------
    # Set Drawing Window
    # -------------------------------------------------

    def set_window(self, x0, y0, x1, y1):

        self.write_cmd(CASET)
        self.write_u16(x0)
        self.write_u16(x1)

        self.write_cmd(RASET)
        self.write_u16(y0)
        self.write_u16(y1)

        self.write_cmd(RAMWR)

    # -------------------------------------------------
    # Write One RGB565 Color
    # -------------------------------------------------

    def write_color(self, color):

        high = (color >> 8) & 0xFF
        low = color & 0xFF

        self.spi.write(bytearray([high, low]))

    # -------------------------------------------------
    # Fill Entire Screen
    # -------------------------------------------------

    def fill_screen(self, color):

        self.set_window(0, 0, WIDTH - 1, HEIGHT - 1)

        self.cs.low()
        self.dc.high()

        for _ in range(WIDTH * HEIGHT):
            self.write_color(color)

        self.cs.high()
        
        
    # -------------------------------------------------
    # Draw Pixel
    # -------------------------------------------------

    def draw_pixel(self, x, y, color):

        # Ignore pixels outside the display
        if x < 0 or x >= WIDTH:
            return

        if y < 0 or y >= HEIGHT:
            return

        self.set_window(x, y, x, y)

        self.cs.low()
        self.dc.high()

        self.write_color(color)

        self.cs.high()
        
        # -------------------------------------------------
    # Draw Line (Bresenham's Algorithm)
    # -------------------------------------------------

    def draw_line(self, x0, y0, x1, y1, color):

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while True:

            self.draw_pixel(x0, y0, color)

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err

            if e2 > -dy:
                err -= dy
                x0 += sx

            if e2 < dx:
                err += dx
                y0 += sy