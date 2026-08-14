from machine import Pin, SPI
from time import sleep

spi = SPI(
    0,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19)
)

cs = Pin(17, Pin.OUT)
cs.value(1)


def write_reg(reg, data):
    cs.value(0)
    spi.write(bytes([reg, data]))
    cs.value(1)


# MAX7219 setup
write_reg(0x0C, 0x01)
write_reg(0x09, 0x00)
write_reg(0x0B, 0x07)
write_reg(0x0A, 0x08)
write_reg(0x0F, 0x00)


# Border pattern
pattern = [
    0b11111111,
    0b10000001,
    0b10000001,
    0b10000001,
    0b10000001,
    0b10000001,
    0b10000001,
    0b11111111
]


# Draw
for row in range(8):
    write_reg(row + 1, pattern[row])


while True:
    sleep(1)