from st7735 import *
from colors import *
from widgets import *

display = ST7735()

display.fill_screen(BLACK)

# ---------------------------------
# Panel
# ---------------------------------

draw_panel(
    display,
    5,
    5,
    118,
    150,
    CYAN,
    title="METER TEST"
)

# ---------------------------------
# 100%
# ---------------------------------

display.draw_text(10, 20, "100%", WHITE)

draw_meter(
    display,
    50,
    18,
    value=100
)

# ---------------------------------
# 75%
# ---------------------------------

display.draw_text(10, 40, "75%", WHITE)

draw_meter(
    display,
    50,
    38,
    value=75
)

# ---------------------------------
# 50%
# ---------------------------------

display.draw_text(10, 60, "50%", WHITE)

draw_meter(
    display,
    50,
    58,
    value=50
)

# ---------------------------------
# 25%
# ---------------------------------

display.draw_text(10, 80, "25%", WHITE)

draw_meter(
    display,
    50,
    78,
    value=25
)

# ---------------------------------
# 0%
# ---------------------------------

display.draw_text(10, 100, "0%", WHITE)

draw_meter(
    display,
    50,
    98,
    value=0
)

# ---------------------------------
# Custom Colors
# ---------------------------------

display.draw_text(10, 125, "CPU", WHITE)

draw_meter(
    display,
    50,
    123,
    value=70,
    filled_color=GREEN,
    empty_color=DARKGRAY
)

display.draw_text(10, 140, "TMP", WHITE)

draw_meter(
    display,
    50,
    138,
    value=90,
    filled_color=RED,
    empty_color=DARKGRAY
)