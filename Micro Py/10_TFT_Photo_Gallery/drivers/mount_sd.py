from machine import Pin, SPI
import sdcard
import os

def mount_sd():

    spi = SPI(
        0,
        baudrate=10_000_000,
        polarity=0,
        phase=0,
        sck=Pin(18),
        mosi=Pin(19),
        miso=Pin(16)
    )

    cs = Pin(5, Pin.OUT)
    cs.value(1)

    sd = sdcard.SDCard(spi, cs)
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")

    print("SD card mounted successfully!")

    return os.listdir("/sd")