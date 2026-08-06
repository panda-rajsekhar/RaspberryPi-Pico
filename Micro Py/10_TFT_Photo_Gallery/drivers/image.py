# Jai Jagannath
# PIMG Image Engine
# Version 1.1

import struct

# -------------------------------------------------
# PIMG Definitions
# -------------------------------------------------

MAGIC = b"PIMG"

PIXEL_RGB565 = 0x01

HEADER_SIZE = 12

DEFAULT_CHUNK_SIZE = 4096


# -------------------------------------------------
# Image Class
# -------------------------------------------------

class Image:

    # ---------------------------------------------
    # Constructor
    # ---------------------------------------------

    def __init__(self, filename):

        self.filename = filename

        self.width = 0
        self.height = 0
        self.pixel_format = 0

        self.file = None

    # ---------------------------------------------
    # Open Image
    # ---------------------------------------------

    def open(self):

        if self.file is None:

            self.file = open(self.filename, "rb")

            self.read_header()

    # ---------------------------------------------
    # Close Image
    # ---------------------------------------------

    def close(self):

        if self.file is not None:

            self.file.close()

            self.file = None

    # ---------------------------------------------
    # Read Header
    # ---------------------------------------------

    def read_header(self):

        magic = self.file.read(4)

        if magic != MAGIC:
            raise ValueError("Invalid PIMG File")

        self.width = struct.unpack("<H", self.file.read(2))[0]

        self.height = struct.unpack("<H", self.file.read(2))[0]

        self.pixel_format = struct.unpack("<B", self.file.read(1))[0]

        # Skip Reserved Bytes
        self.file.read(3)

    # ---------------------------------------------
    # Image Information
    # ---------------------------------------------

    def info(self):

        print("--------------------------------")
        print("PIMG Image Information")
        print("--------------------------------")

        print("File   :", self.filename)
        print("Width  :", self.width)
        print("Height :", self.height)

        if self.pixel_format == PIXEL_RGB565:
            print("Format : RGB565")
        else:
            print("Format : Unknown")

        print("--------------------------------")

    # ---------------------------------------------
    # Draw Image
    # ---------------------------------------------

    def draw(self, display, x, y, chunk_size=DEFAULT_CHUNK_SIZE):

        self.open()

        if self.pixel_format != PIXEL_RGB565:

            self.close()

            raise ValueError("Unsupported Pixel Format")

        display.set_window(
            x,
            y,
            x + self.width - 1,
            y + self.height - 1
        )

        buffer = bytearray(chunk_size)

        while True:

            count = self.file.readinto(buffer)

            if count == 0:
                break

            if count == chunk_size:

                display.write_buffer(buffer)

            else:

                display.write_buffer(memoryview(buffer)[:count])

        self.close()