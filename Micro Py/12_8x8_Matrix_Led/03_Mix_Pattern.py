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

def show(pattern):
    for row in range(8):
        write_reg(row + 1, pattern[row])

# --- MAX7219 setup ---
write_reg(0x0C, 0x01)  # shutdown -> normal operation
write_reg(0x09, 0x00)  # decode mode -> no decode (raw bitmap)
write_reg(0x0B, 0x07)  # scan limit -> all 8 digits/rows
write_reg(0x0A, 0x08)  # intensity (0x00 dim - 0x0F bright)
write_reg(0x0F, 0x00)  # display test -> off

# --- Patterns ---
CHECKERBOARD = [0b10101010, 0b01010101] * 4

HEART = [
    0b01100110,
    0b11111111,
    0b11111111,
    0b11111111,
    0b01111110,
    0b00111100,
    0b00011000,
    0b00000000,
]

SMILEY = [
    0b00111100,
    0b01000010,
    0b10100101,
    0b10000001,
    0b10100101,
    0b10011001,
    0b01000010,
    0b00111100,
]

ARROW_UP = [
    0b00011000,
    0b00111100,
    0b01111110,
    0b11011011,
    0b00011000,
    0b00011000,
    0b00011000,
    0b00011000,
]

X_MARK = [
    0b10000001,
    0b01000010,
    0b00100100,
    0b00011000,
    0b00011000,
    0b00100100,
    0b01000010,
    0b10000001,
]

ALL_OFF = [0b00000000] * 8
ALL_ON  = [0b11111111] * 8

def diagonal_wipe_in(pattern, delay=0.03):
    """Reveal a pattern one diagonal at a time (top-left to bottom-right)."""
    frame = [0] * 8
    for d in range(15):  # 0..14 covers all row+col diagonals for 8x8
        for row in range(8):
            for col in range(8):
                if row + col == d:
                    bit = (pattern[row] >> (7 - col)) & 1
                    if bit:
                        frame[row] |= (1 << (7 - col))
        show(frame)
        sleep(delay)

def spiral_fill(delay=0.05):
    """Fill the matrix in a spiral, then unfill the same way."""
    frame = [[0] * 8 for _ in range(8)]
    top, bottom, left, right = 0, 7, 0, 7
    coords = []
    while top <= bottom and left <= right:
        coords += [(top, c) for c in range(left, right + 1)]
        top += 1
        coords += [(r, right) for r in range(top, bottom + 1)]
        right -= 1
        if top <= bottom:
            coords += [(bottom, c) for c in range(right, left - 1, -1)]
            bottom -= 1
        if left <= right:
            coords += [(r, left) for r in range(bottom, top - 1, -1)]
            left += 1

    for r, c in coords:
        frame[r][c] = 1
        show([sum(v << (7 - i) for i, v in enumerate(row)) for row in frame])
        sleep(delay)

    for r, c in coords:
        frame[r][c] = 0
        show([sum(v << (7 - i) for i, v in enumerate(row)) for row in frame])
        sleep(delay)

def pulse(pattern, cycles=2, delay=0.4):
    for _ in range(cycles):
        show(pattern)
        sleep(delay)
        show(ALL_OFF)
        sleep(delay / 2)

# --- Main animation loop ---
while True:
    diagonal_wipe_in(SMILEY)
    sleep(1)
    show(ALL_OFF)
    sleep(0.3)

    pulse(HEART, cycles=3, delay=0.35)
    sleep(0.3)

    spiral_fill(delay=0.04)
    sleep(0.3)

    show(X_MARK)
    sleep(1)
    show(ALL_OFF)
    sleep(0.3)

    show(CHECKERBOARD)
    sleep(1)
    show(ALL_OFF)
    sleep(0.3)