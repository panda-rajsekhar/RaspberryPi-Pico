from st7735 import *
from colors import *
from widgets import *

display = ST7735()

display.fill_screen(BLACK)

history = [
    10,20,15,35,50,40,60,55,
    70,65,80,60,45,35,20,10
]

draw_panel(
    display,
    5,
    5,
    118,
    70,
    CYAN,
    title="CPU HISTORY"
)

draw_graph(
    display,
    10,
    25,
    108,
    40,
    history,
    GREEN
)