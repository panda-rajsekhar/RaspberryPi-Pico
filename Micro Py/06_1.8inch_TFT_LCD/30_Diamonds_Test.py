from st7735 import *
from colors import *
from widgets import *

display = ST7735()

display.fill_screen(BLACK)

draw_panel(
    display,
    5,
    5,
    118,
    150,
    CYAN,
    title="DIAMOND TEST"
)

# -------------------------
# Filled Diamonds
# -------------------------

draw_diamond(display, 15, 20, 9, RED, True)
draw_diamond(display, 30, 20, 9, GREEN, True)
draw_diamond(display, 45, 20, 9, BLUE, True)
draw_diamond(display, 60, 20, 9, YELLOW, True)
draw_diamond(display, 75, 20, 9, CYAN, True)
draw_diamond(display, 90, 20, 9, MAGENTA, True)

# -------------------------
# Outline Diamonds
# -------------------------

draw_diamond(display, 15, 45, 9, RED, False)
draw_diamond(display, 30, 45, 9, GREEN, False)
draw_diamond(display, 45, 45, 9, BLUE, False)
draw_diamond(display, 60, 45, 9, YELLOW, False)
draw_diamond(display, 75, 45, 9, CYAN, False)
draw_diamond(display, 90, 45, 9, MAGENTA, False)

# -------------------------
# Different Sizes
# -------------------------

draw_diamond(display, 15, 75, 5, GREEN, True)
draw_diamond(display, 30, 72, 9, GREEN, True)
draw_diamond(display, 50, 68, 13, GREEN, True)
draw_diamond(display, 75, 63, 19, GREEN, True)

# -------------------------
# Meter Preview
# -------------------------

for i in range(10):

    if i < 7:
        draw_diamond(
            display,
            12 + i * 11,
            120,
            9,
            GREEN,
            True
        )
    else:
        draw_diamond(
            display,
            12 + i * 11,
            120,
            9,
            DARKGRAY,
            False
        )