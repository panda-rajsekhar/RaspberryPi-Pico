# Jai Jagannath
# SD Card Status Utility

from machine import Pin, SPI
import sdcard
import os

print("--------------------------------")
print("SD Card Status")
print("--------------------------------")

try:
    # SPI Configuration
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

    # Initialize SD
    sd = sdcard.SDCard(spi, cs)
    vfs = os.VfsFat(sd)

    try:
        os.mount(vfs, "/sd")
    except OSError:
        # Already mounted
        pass

    print("Status : Mounted")
    print("Mount  : /sd")
    print("--------------------------------")
    print("Contents")

    files = os.listdir("/sd")

    if not files:
        print(" <Empty>")
    else:
        for file in files:
            print(" -", file)

except Exception as e:

    print("Status : Not Available")
    print("Reason :", e)

print("--------------------------------")