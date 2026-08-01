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
    45,
    CYAN,
    title="SYSTEM"
)

draw_panel(
    display,
    5,
    60,
    118,
    45,
    GREEN,
    title="NETWORK"
)

draw_panel(
    display,
    5,
    115,
    118,
    40,
    RED,
    title="STATUS"
)