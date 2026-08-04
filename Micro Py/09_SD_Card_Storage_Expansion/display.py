from machine import Pin, SPI
import os
import sdcard

from st7735 import ST7735
from image import Image

# ------------------------
# Initialize TFT
# ------------------------
display = ST7735()
display.fill_screen(0x0000)

# ------------------------
# Mount SD Card
# ------------------------
spi = SPI(
    0,
    baudrate=100000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),
    miso=Pin(16)
)

cs = Pin(5, Pin.OUT)
cs.value(1)

try:
    sd = sdcard.SDCard(spi, cs)
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
except OSError:
    pass

print(os.listdir("/sd"))

# ------------------------
# Load image
# ------------------------
img = Image("/sd/test.pimg")

img.open()
img.info()          # Print image information
img.close()

# ------------------------
# Draw image
# ------------------------
img.draw(display, 0, 0)

print("Image displayed!")