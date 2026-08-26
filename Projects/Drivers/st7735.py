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
    
    def __init__(self,spi_id=0,baudrate=20_000_000,sck=18,mosi=19,cs=17,dc=21,rst=20):
        self.spi = SPI(
        spi_id,
        baudrate=baudrate,
        polarity=0,
        phase=0,
        sck=Pin(sck),
        mosi=Pin(mosi))

        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)

        self.cs.high()
        self.dc.high()
        self.rst.high()

        # -----------------------------------------
        # Reusable Buffers
        # -----------------------------------------

        # Single pixel buffer
        self.pixel_buffer = bytearray(2)

        # 6x8 character buffer (RGB565)
        self.char_buffer = bytearray(6 * 8 * 2)
        
        # fastest :-) Buffer Scanline 
        self.scanline = bytearray(1024)

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

        self.pixel_buffer[0] = (color >> 8) & 0xFF
        self.pixel_buffer[1] = color & 0xFF

        self.spi.write(self.pixel_buffer)

    # -------------------------------------------------
    # Fill Entire Screen
    # -------------------------------------------------

    def fill_screen(self, color):

        self.set_window(0, 0, WIDTH - 1, HEIGHT - 1)

        high = (color >> 8) & 0xFF
        low = color & 0xFF

        # One full display row
        row = bytearray(WIDTH * 2)

        for i in range(0, len(row), 2):
            row[i] = high
            row[i + 1] = low

        self.cs.low()
        self.dc.high()

        for _ in range(HEIGHT):
            self.spi.write(row)

        self.cs.high()
        
        
    # -------------------------------------------------
    # Draw Pixel
    # -------------------------------------------------

    def draw_pixel(self, x, y, color):

        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return

        self.set_window(x, y, x, y)

        self.cs.low()
        self.dc.high()

        self.spi.write(bytes((
            (color >> 8) & 0xFF,
            color & 0xFF
        )))

        self.cs.high()
        
    # -------------------------------------------------
    # Draw Line
    # -------------------------------------------------

    def draw_line(self, x0, y0, x1, y1, color):

        # -----------------------------------------
        # Horizontal Line
        # -----------------------------------------

        if y0 == y1:

            if x1 < x0:
                x0, x1 = x1, x0

            self.draw_hline(
                x0,
                y0,
                x1 - x0 + 1,
                color
            )

            return

        # -----------------------------------------
        # Vertical Line
        # -----------------------------------------

        if x0 == x1:

            if y1 < y0:
                y0, y1 = y1, y0

            self.draw_vline(
                x0,
                y0,
                y1 - y0 + 1,
                color
            )

            return

        # -----------------------------------------
        # General Line (Bresenham)
        # -----------------------------------------

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while True:

            self.draw_pixel(
                x0,
                y0,
                color
            )

            if x0 == x1 and y0 == y1:
                break

            e2 = err << 1

            if e2 > -dy:
                err -= dy
                x0 += sx

            if e2 < dx:
                err += dx
                y0 += sy

    # -------------------------------------------------
    # Fast Horizontal Line
    # -------------------------------------------------

    def draw_hline(self, x, y, length, color):

        if length <= 0:
            return

        self.set_window(
            x,
            y,
            x + length - 1,
            y
        )

        hi = (color >> 8) & 0xFF
        lo = color & 0xFF

        row = self.scanline

        for i in range(0, length * 2, 2):
            row[i] = hi
            row[i + 1] = lo

        self.cs.low()
        self.dc.high()
        self.spi.write(memoryview(row)[:length * 2])
        self.cs.high()

    # -------------------------------------------------
    # Fast Vertical Line
    # -------------------------------------------------

    def draw_vline(self, x, y, length, color):

        if length <= 0:
            return

        self.set_window(
            x,
            y,
            x,
            y + length - 1
        )

        hi = (color >> 8) & 0xFF
        lo = color & 0xFF

        self.pixel_buffer[0] = hi
        self.pixel_buffer[1] = lo

        self.cs.low()
        self.dc.high()

        for _ in range(length):
            self.spi.write(self.pixel_buffer)

        self.cs.high()  
    # -------------------------------------------------
    # Draw Rectangle
    # -------------------------------------------------

    def draw_rectangle(self, x, y, width, height, color):

        # Invalid rectangle
        if width <= 0 or height <= 0:
            return

        # Completely outside screen
        if (x >= WIDTH or
            y >= HEIGHT or
            x + width <= 0 or
            y + height <= 0):
            return

        # Top
        self.draw_hline(
            x,
            y,
            width,
            color
        )

        # Bottom (only if height > 1)
        if height > 1:

            self.draw_hline(
                x,
                y + height - 1,
                width,
                color
            )

        # Left
        if height > 2:

            self.draw_vline(
                x,
                y + 1,
                height - 2,
                color
            )

        # Right (only if width > 1)
        if width > 1 and height > 2:

            self.draw_vline(
                x + width - 1,
                y + 1,
                height - 2,
                color
            )
        
    # -------------------------------------------------
    # Fill Rectangle (Optimized)
    # -------------------------------------------------

    def fill_rectangle(self, x, y, width, height, color):

        # Clip to display boundaries
        if x < 0:
            width += x
            x = 0

        if y < 0:
            height += y
            y = 0

        if x + width > WIDTH:
            width = WIDTH - x

        if y + height > HEIGHT:
            height = HEIGHT - y

        if width <= 0 or height <= 0:
            return

        # Set drawing window ONLY ONCE
        self.set_window(
            x,
            y,
            x + width - 1,
            y + height - 1
        )

        high = (color >> 8) & 0xFF
        low = color & 0xFF

        # One row buffer
        row = bytearray(width * 2)

        for i in range(0, len(row), 2):
            row[i] = high
            row[i + 1] = low

        self.cs.low()
        self.dc.high()

        for _ in range(height):
            self.spi.write(row)

        self.cs.high()

    # -------------------------------------------------
    # Draw Circle (Midpoint Circle Algorithm)
    # -------------------------------------------------

    def draw_circle(self, xc, yc, radius, color):

        if radius <= 0:
            return

        x = radius
        y = 0
        decision = 1 - radius

        while x >= y:

            # Octant 1
            self.draw_pixel(xc + x, yc + y, color)
            self.draw_pixel(xc - x, yc + y, color)
            self.draw_pixel(xc + x, yc - y, color)
            self.draw_pixel(xc - x, yc - y, color)

            # Octant 2
            self.draw_pixel(xc + y, yc + x, color)
            self.draw_pixel(xc - y, yc + x, color)
            self.draw_pixel(xc + y, yc - x, color)
            self.draw_pixel(xc - y, yc - x, color)

            y += 1

            if decision < 0:

                decision += (y << 1) + 1

            else:

                x -= 1
                decision += ((y - x) << 1) + 1
    # -------------------------------------------------
    # Fill Circle
    # -------------------------------------------------

    def fill_circle(self, xc, yc, radius, color):
        if radius <= 0:
            return

        x = radius
        y = 0
        decision = 1 - radius

        while x >= y:
            self.draw_hline(xc - x, yc + y, 2 * x + 1, color)
            self.draw_hline(xc - x, yc - y, 2 * x + 1, color)
            self.draw_hline(xc - y, yc + x, 2 * y + 1, color)
            self.draw_hline(xc - y, yc - x, 2 * y + 1, color)

            y += 1

            if decision <= 0:
                decision += (y << 1) + 1
            else:
                x -= 1
                decision += ((y - x) << 1) + 1

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
    # Draw Character (Optimized)
    # -------------------------------------------------

    def draw_char(self, x, y, char, color, size=1, bg_color=None):

        index = (ord(char) - 32) * 5

        if index < 0 or index >= len(FONT_5X7):
            return

        # Fallback for scaled fonts
        # -------------------------------------------------
        # Fast renderer (size = 1)
        # -------------------------------------------------

        if size == 1:

            if bg_color is None:
                bg_color = BLACK

            fg_hi = (color >> 8) & 0xFF
            fg_lo = color & 0xFF

            bg_hi = (bg_color >> 8) & 0xFF
            bg_lo = bg_color & 0xFF

            p = 0

            # Build one complete 6x8 RGB565 character
            for row in range(8):

                for col in range(5):

                    line = FONT_5X7[index + col]

                    if line & (1 << row):

                        self.char_buffer[p] = fg_hi
                        self.char_buffer[p + 1] = fg_lo

                    else:

                        self.char_buffer[p] = bg_hi
                        self.char_buffer[p + 1] = bg_lo

                    p += 2

                # Spacing column
                self.char_buffer[p] = bg_hi
                self.char_buffer[p + 1] = bg_lo
                p += 2

            # Draw the whole character in one SPI transfer
            self.set_window(
                x,
                y,
                x + 5,
                y + 7
            )

            self.cs.low()
            self.dc.high()
            self.spi.write(self.char_buffer)
            self.cs.high()

            return

        # -------------------------------
        # Fast path (size == 1)
        # -------------------------------

        width = 6
        height = 8

        fg_hi = (color >> 8) & 0xFF
        fg_lo = color & 0xFF

        if bg_color is None:
            bg_hi = 0
            bg_lo = 0
        else:
            bg_hi = (bg_color >> 8) & 0xFF
            bg_lo = bg_color & 0xFF

        buffer = bytearray(width * height * 2)

        p = 0

        for row in range(8):

            for col in range(5):

                line = FONT_5X7[index + col]

                if line & (1 << row):

                    buffer[p] = fg_hi
                    buffer[p + 1] = fg_lo

                else:

                    if bg_color is None:
                        buffer[p] = 0
                        buffer[p + 1] = 0
                    else:
                        buffer[p] = bg_hi
                        buffer[p + 1] = bg_lo

                p += 2

            # spacing column

            if bg_color is None:
                buffer[p] = 0
                buffer[p + 1] = 0
            else:
                buffer[p] = bg_hi
                buffer[p + 1] = bg_lo

            p += 2

        self.set_window(
            x,
            y,
            x + width - 1,
            y + height - 1
        )

        self.cs.low()
        self.dc.high()
        self.spi.write(buffer)
        self.cs.high()
                
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
    # Fast Text Renderer (Scanline Buffered)
    # -------------------------------------------------

    def draw_text_fast(self, x, y, text, color, bg_color=BLACK):

        if not text:
            return

        # -----------------------------------------
        # Clip text to screen width
        # -----------------------------------------

        max_chars = (WIDTH - x) // 6

        if max_chars <= 0:
            return

        if len(text) > max_chars:

            if max_chars > 3:
                text = text[:max_chars - 3] + "..."
            else:
                text = text[:max_chars]

        width = len(text) * 6

        # -----------------------------------------
        # Set drawing window
        # -----------------------------------------

        self.set_window(
            x,
            y,
            x + width - 1,
            y + 7
        )

        fg_hi = (color >> 8) & 0xFF
        fg_lo = color & 0xFF

        bg_hi = (bg_color >> 8) & 0xFF
        bg_lo = bg_color & 0xFF

        self.cs.low()
        self.dc.high()

        # -----------------------------------------
        # Render one scanline at a time
        # -----------------------------------------

        for row in range(8):

            p = 0

            for ch in text:

                index = (ord(ch) - 32) * 5

                # Invalid character -> blank
                if index < 0 or (index + 4) >= len(FONT_5X7):

                    for _ in range(6):
                        self.scanline[p] = bg_hi
                        self.scanline[p + 1] = bg_lo
                        p += 2

                    continue

                # Five font columns
                for col in range(5):

                    line = FONT_5X7[index + col]

                    if line & (1 << row):

                        self.scanline[p] = fg_hi
                        self.scanline[p + 1] = fg_lo

                    else:

                        self.scanline[p] = bg_hi
                        self.scanline[p + 1] = bg_lo

                    p += 2

                # Character spacing
                self.scanline[p] = bg_hi
                self.scanline[p + 1] = bg_lo
                p += 2

            # Write one complete scanline
            self.spi.write(memoryview(self.scanline)[:p])

        self.cs.high()
    # -------------------------------------------------
    # Write Raw RGB565 Buffer
    # -------------------------------------------------

    def write_buffer(self, buffer):

        self.cs.low()
        self.dc.high()

        self.spi.write(buffer)

        self.cs.high()
        
    # -------------------------------------------------
    # Stream RGB565 Pixel
    # -------------------------------------------------

    def stream_color(self, color):

        self.pixel_buffer[0] = (color >> 8) & 0xFF
        self.pixel_buffer[1] = color & 0xFF

        self.spi.write(self.pixel_buffer)


