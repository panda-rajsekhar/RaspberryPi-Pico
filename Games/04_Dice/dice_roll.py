from machine import Pin, SPI
from time import sleep, ticks_ms, ticks_diff
import random

# --- Matrix (SPI0) ---
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

# --- Button (active LOW: press connects pin to GND) ---
button = Pin(16, Pin.IN, Pin.PULL_UP)

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
write_reg(0x0B, 0x07)  # scan limit -> all 8 rows
write_reg(0x0A, 0x08)  # intensity
write_reg(0x0F, 0x00)  # display test -> off

# --- Dice faces: pips on a 3x3 grid at rows/cols 1, 3, 5 ---
FACES = {
    1: [0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00],  # center
    2: [0x00, 0x40, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00],  # diagonal
    3: [0x00, 0x40, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00],  # diagonal + center
    4: [0x00, 0x44, 0x00, 0x00, 0x00, 0x44, 0x00, 0x00],  # four corners
    5: [0x00, 0x44, 0x00, 0x10, 0x00, 0x44, 0x00, 0x00],  # corners + center
    6: [0x00, 0x44, 0x00, 0x44, 0x00, 0x44, 0x00, 0x00],  # two columns of 3
}
ALL_OFF = [0x00] * 8

def roll_animation(duration_ms=600, step_ms=60):
    """Flash random faces quickly to simulate the die tumbling."""
    t0 = ticks_ms()
    while ticks_diff(ticks_ms(), t0) < duration_ms:
        show(FACES[random.randint(1, 6)])
        sleep(step_ms / 1000)

def wait_for_press():
    """Blocks until button is pressed, with simple debounce."""
    while button.value() == 1:
        sleep(0.01)
    sleep(0.03)  # debounce
    return button.value() == 0

def wait_for_release():
    while button.value() == 0:
        sleep(0.01)
    sleep(0.03)  # debounce

# --- Main loop ---
show(ALL_OFF)

while True:
    if wait_for_press():
        roll_animation(duration_ms=600, step_ms=60)
        result = random.randint(1, 6)
        show(FACES[result])
        print("Rolled:", result)
        wait_for_release()