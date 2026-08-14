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
write_reg(0x0C, 0x01)   # Normal operation
write_reg(0x09, 0x00)   # No decode
write_reg(0x0B, 0x07)   # Scan all 8 rows
write_reg(0x0A, 0x08)   # Brightness
write_reg(0x0F, 0x00)   # Display test OFF


# X pattern
pattern = [
    0b10000001,
    0b01000010,
    0b00100100,
    0b00011000,
    0b00011000,
    0b00100100,
    0b01000010,
    0b10000001
]


# Draw pattern
for row in range(8):
    write_reg(row + 1, pattern[row])


while True:
    sleep(1)