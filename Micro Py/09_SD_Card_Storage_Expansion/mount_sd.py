from machine import Pin, SPI
import sdcard
import os

# SPI0 Configuration
spi = SPI(
    0,
    baudrate=100000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),
    miso=Pin(16)
)

# SD Card Chip Select (your working pin)
cs = Pin(5, Pin.OUT)
cs.value(1)

# Initialize and mount
sd = sdcard.SDCard(spi, cs)
vfs = os.VfsFat(sd)
os.mount(vfs, "/sd")

print("SD card mounted successfully!")
print(os.listdir("/sd"))