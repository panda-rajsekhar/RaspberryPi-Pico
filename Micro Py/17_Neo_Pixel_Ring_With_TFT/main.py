import time
from machine import Pin
import neopixel

from st7735 import ST7735
from colors import BLACK, WHITE, CYAN, GREEN, YELLOW, RED, BLUE


# ============================================================
# Configuration
# ============================================================

LED_PIN = 15
NUM_LEDS = 8

MODE_TIME_MS = 3000

ring = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)
display = ST7735()


# ============================================================
# Rainbow
# ============================================================

def wheel(pos):
    pos = 255 - pos

    if pos < 85:
        return (
            255 - pos * 3,
            0,
            pos * 3
        )

    if pos < 170:
        pos -= 85
        return (
            0,
            pos * 3,
            255 - pos * 3
        )

    pos -= 170

    return (
        pos * 3,
        255 - pos * 3,
        0
    )


def rainbow(offset):

    for i in range(NUM_LEDS):

        color = wheel(
            (i * 256 // NUM_LEDS + offset) & 255
        )

        # 25% brightness
        ring[i] = (
            color[0] // 4,
            color[1] // 4,
            color[2] // 4
        )

    ring.write()


# ============================================================
# Other Effects
# ============================================================

def solid(color):

    ring.fill(color)
    ring.write()


def off():

    ring.fill((0, 0, 0))
    ring.write()


# ============================================================
# TFT UI
# ============================================================

def show_mode(mode, number):

    display.fill_screen(BLACK)

    display.draw_text_fast(
        8, 10,
        "WS2812 RING",
        CYAN,
        BLACK
    )

    display.draw_text_fast(
        8, 35,
        "MODE",
        WHITE,
        BLACK
    )

    display.draw_text_fast(
        8, 55,
        mode,
        GREEN,
        BLACK
    )

    display.draw_text_fast(
        8, 85,
        "MODE {}".format(number),
        YELLOW,
        BLACK
    )

    display.draw_text_fast(
        8, 120,
        "PICO + ST7735",
        RED,
        BLACK
    )


# ============================================================
# Main
# ============================================================

modes = [
    "RAINBOW",
    "RED",
    "GREEN",
    "BLUE",
    "WHITE"
]

mode_index = 0
mode_start = time.ticks_ms()

show_mode(modes[mode_index], mode_index + 1)

offset = 0

while True:

    # --------------------------------------------------------
    # Rainbow animation
    # --------------------------------------------------------

    if mode_index == 0:

        rainbow(offset)

        offset = (offset + 2) & 255

        time.sleep_ms(30)

    # --------------------------------------------------------
    # Static colors
    # --------------------------------------------------------

    elif mode_index == 1:

        solid((40, 0, 0))
        time.sleep_ms(50)

    elif mode_index == 2:

        solid((0, 40, 0))
        time.sleep_ms(50)

    elif mode_index == 3:

        solid((0, 0, 40))
        time.sleep_ms(50)

    elif mode_index == 4:

        solid((20, 20, 20))
        time.sleep_ms(50)

    # --------------------------------------------------------
    # Change mode
    # --------------------------------------------------------

    if time.ticks_diff(
        time.ticks_ms(),
        mode_start
    ) >= MODE_TIME_MS:

        mode_index += 1

        if mode_index >= len(modes):
            mode_index = 0

        mode_start = time.ticks_ms()
        offset = 0

        show_mode(
            modes[mode_index],
            mode_index + 1
        )