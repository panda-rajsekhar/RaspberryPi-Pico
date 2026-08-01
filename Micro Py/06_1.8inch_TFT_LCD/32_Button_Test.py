from st7735 import *
from colors import *
from widgets import *

display = ST7735()

display.fill_screen(BLACK)

# -------------------------------------------------
# Title
# -------------------------------------------------

draw_panel(
    display,
    3,
    3,
    122,
    154,
    CYAN,
    title="BUTTON TEST"
)

# -------------------------------------------------
# Normal Buttons
# -------------------------------------------------

draw_button(
    display,
    10,
    20,
    45,
    20,
    "OK"
)

draw_button(
    display,
    70,
    20,
    45,
    20,
    "BACK"
)

# -------------------------------------------------
# Colored Buttons
# -------------------------------------------------

draw_button(
    display,
    10,
    50,
    45,
    20,
    "RUN",
    border_color=GREEN
)

draw_button(
    display,
    70,
    50,
    45,
    20,
    "STOP",
    border_color=RED
)

# -------------------------------------------------
# Pressed Buttons
# -------------------------------------------------

draw_button(
    display,
    10,
    80,
    45,
    20,
    "YES",
    border_color=GREEN,
    pressed=True
)

draw_button(
    display,
    70,
    80,
    45,
    20,
    "NO",
    border_color=RED,
    pressed=True
)

# -------------------------------------------------
# Large Button
# -------------------------------------------------

draw_button(
    display,
    18,
    115,
    92,
    26,
    "START",
    border_color=CYAN
)