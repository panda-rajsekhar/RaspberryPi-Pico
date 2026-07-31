from machine import Pin, SPI
from time import sleep_ms

spi = SPI(
    0,
    baudrate=20_000_000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19)
)

cs = Pin(17, Pin.OUT)
dc = Pin(21, Pin.OUT)
rst = Pin(20, Pin.OUT)

cs.high()
dc.high()
rst.high()


def hardware_reset():
    rst.high()
    sleep_ms(5)
    rst.low()
    sleep_ms(20)
    rst.high()
    sleep_ms(150)


def write_cmd(cmd):
    cs.low()
    dc.low()
    spi.write(bytearray([cmd]))
    cs.high()


def write_data(data):
    cs.low()
    dc.high()
    spi.write(bytearray([data]))
    cs.high()


hardware_reset()

write_cmd(0x01)
sleep_ms(150)

write_cmd(0x11)
sleep_ms(150)

write_cmd(0x29)
sleep_ms(100)
