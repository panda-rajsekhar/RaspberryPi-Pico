from machine import Pin, SPI
import os
import sdcard

# ----------------------------
# Mount SD card
# ----------------------------
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
    # Already mounted
    pass

# ----------------------------
# Copy file
# ----------------------------
src = "/test.pimg"
dst = "/sd/test.pimg"

with open(src, "rb") as fsrc:
    with open(dst, "wb") as fdst:
        while True:
            data = fsrc.read(512)
            if not data:
                break
            fdst.write(data)

print("✅ Copied successfully!")

print("Root:", os.listdir("/"))
print("SD:", os.listdir("/sd"))