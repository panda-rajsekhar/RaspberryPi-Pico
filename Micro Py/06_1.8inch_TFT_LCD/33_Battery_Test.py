from st7735 import *
from colors import *
from widgets import *

display = ST7735()

display.fill_screen(BLACK)

draw_panel(
    display,
    3,
    3,
    122,
    154,
    CYAN,
    title="BATTERY TEST"
)

levels = [100, 75, 50, 25, 10, 0]

y = 20

for level in levels:

    display.draw_text(
        10,
        y + 3,
        str(level) + "%",
        WHITE
    )

    # Automatic battery color
    if level > 50:
        color = GREEN
    elif level > 20:
        color = YELLOW
    else:
        color = RED

    draw_battery(
        display,
        50,
        y,
        level,
        fill_color=color
    )

    y += 22