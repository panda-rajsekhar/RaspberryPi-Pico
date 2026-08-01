from st7735 import *
from colors import *
from time import sleep_ms

display = ST7735()

display.fill_screen(NAVY)

# ----------------------------------
# Transparent Text
# ----------------------------------

display.draw_text(
    10,
    10,
    "TRANSPARENT",
    YELLOW
)

sleep_ms(1500)

# ----------------------------------
# Background Text
# ----------------------------------

display.draw_text(
    10,
    30,
    "BACKGROUND",
    WHITE,
    bg_color=RED
)

sleep_ms(1500)

# ----------------------------------
# Dynamic Counter
# ----------------------------------

for i in range(100):

    display.draw_text(
        10,
        60,
        "COUNT : {:02}".format(i),
        CYAN,
        bg_color=BLACK
    )

    sleep_ms(100)