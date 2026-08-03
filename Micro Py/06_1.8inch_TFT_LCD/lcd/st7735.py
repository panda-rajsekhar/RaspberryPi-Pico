#Jai Jagannath
#Its is an attempt to make a useful HMI 

from machine import Pin, SPI
from time import sleep_ms
from colors import *
from fonts import *
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
        baudrate = 20_000_000,
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
        
    # -------------------------------------------------
    # Draw Rectangle
    # -------------------------------------------------

    def draw_rectangle(self, x, y, width, height, color):

        # Top
        self.draw_line(x, y, x + width - 1, y, color)

        # Bottom
        self.draw_line(x, y + height - 1,
                       x + width - 1,
                       y + height - 1,
                       color)

        # Left
        self.draw_line(x, y, x, y + height - 1, color)

        # Right
        self.draw_line(x + width - 1,
                       y,
                       x + width - 1,
                       y + height - 1,
                       color)
        
    # -------------------------------------------------
    # Fill Rectangle
    # -------------------------------------------------

    def fill_rectangle(self, x, y, width, height, color):

        for row in range(height):

            self.draw_line(
                x,
                y + row,
                x + width - 1,
                y + row,
                color
            )
            
    # -------------------------------------------------
    # Draw Circle (Midpoint Circle Algorithm)
    # -------------------------------------------------

    def draw_circle(self, xc, yc, radius, color):

        x = radius
        y = 0

        decision = 1 - radius

        while x >= y:

            self.draw_pixel(xc + x, yc + y, color)
            self.draw_pixel(xc - x, yc + y, color)
            self.draw_pixel(xc + x, yc - y, color)
            self.draw_pixel(xc - x, yc - y, color)

            self.draw_pixel(xc + y, yc + x, color)
            self.draw_pixel(xc - y, yc + x, color)
            self.draw_pixel(xc + y, yc - x, color)
            self.draw_pixel(xc - y, yc - x, color)

            y += 1

            if decision <= 0:
                decision += 2 * y + 1
            else:
                x -= 1
                decision += 2 * (y - x) + 1
                
                
    # -------------------------------------------------
    # Fill Circle
    # -------------------------------------------------

    def fill_circle(self, xc, yc, radius, color):

        x = radius
        y = 0

        decision = 1 - radius

        while x >= y:

            self.draw_line(xc - x, yc + y, xc + x, yc + y, color)
            self.draw_line(xc - x, yc - y, xc + x, yc - y, color)

            self.draw_line(xc - y, yc + x, xc + y, yc + x, color)
            self.draw_line(xc - y, yc - x, xc + y, yc - x, color)

            y += 1

            if decision <= 0:
                decision += 2 * y + 1
            else:
                x -= 1
                decision += 2 * (y - x) + 1
                
    # -------------------------------------------------
    # Draw Triangle
    # -------------------------------------------------

    def draw_triangle(self, x0, y0, x1, y1, x2, y2, color):

        self.draw_line(x0, y0, x1, y1, color)
        self.draw_line(x1, y1, x2, y2, color)
        self.draw_line(x2, y2, x0, y0, color)
        
    # -------------------------------------------------
    # Fill Triangle (Scanline Algorithm)
    # -------------------------------------------------

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):

        # Sort vertices by Y coordinate
        if y0 > y1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        if y0 > y1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        def interpolate(y, x_start, y_start, x_end, y_end):
            if y_end == y_start:
                return x_start
            return int(
                x_start +
                (x_end - x_start) *
                (y - y_start) /
                (y_end - y_start)
            )

        for y in range(y0, y2 + 1):

            if y < y1:
                xa = interpolate(y, x0, y0, x1, y1)
                xb = interpolate(y, x0, y0, x2, y2)
            else:
                xa = interpolate(y, x1, y1, x2, y2)
                xb = interpolate(y, x0, y0, x2, y2)

            if xa > xb:
                xa, xb = xb, xa

            self.draw_line(xa, y, xb, y, color)
       
    # -------------------------------------------------
    # Draw Character
    # -------------------------------------------------

    def draw_char(self, x, y, char, color, size=1, bg_color=None):

        index = (ord(char) - 32) * 5

        if index < 0 or index >= len(FONT_5X7):
            return

        for col in range(5):

            line = FONT_5X7[index + col]

            for row in range(8):

                if line & (1 << row):
                    pixel = color
                else:
                    pixel = bg_color

                if pixel is None:
                    continue

                if size == 1:

                    self.draw_pixel(
                        x + col,
                        y + row,
                        pixel
                    )

                else:

                    self.fill_rectangle(
                        x + col * size,
                        y + row * size,
                        size,
                        size,
                        pixel
                    )

        # Draw the spacing column
        if bg_color is not None:

            if size == 1:

                for row in range(8):
                    self.draw_pixel(
                        x + 5,
                        y + row,
                        bg_color
                    )

            else:

                self.fill_rectangle(
                    x + 5 * size,
                    y,
                    size,
                    8 * size,
                    bg_color
                )
                
    # -------------------------------------------------
    # Draw Text
    # -------------------------------------------------

    def draw_text(self, x, y, text, color, size=1, bg_color=None):

        start_x = x

        for char in text:

            if char == "\n":

                y += 8 * size
                x = start_x
                continue

            self.draw_char(
                x,
                y,
                char,
                color,
                size,
                bg_color
            )

            x += 6 * size
    # -------------------------------------------------
    # Write Raw RGB565 Buffer
    # -------------------------------------------------

    def write_buffer(self, buffer):

        self.cs.low()
        self.dc.high()

        self.spi.write(buffer)

        self.cs.high()


    
    
