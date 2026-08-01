from st7735 import *
from colors import *
from time import sleep_ms

display = ST7735()

display.fill_screen(BLACK)

# -------------------------
# Progress Bar Dimensions
# -------------------------

bar_x = 14
bar_y = 72

bar_width = 100
bar_height = 16

# Draw Border
display.draw_rectangle(
    bar_x,
    bar_y,
    bar_width,
    bar_height,
    WHITE
)

display.draw_text(30, 40, "Raspberry Pi", WHITE)
display.draw_text(25, 52, "Pico RP2040", CYAN)
# -------------------------
# Loading Animation
# -------------------------

for progress in range(bar_width + 1):

    display.fill_rectangle(
        bar_x + 1,
        bar_y + 1,
        progress - 2,
        bar_height - 2,
        GREEN
    )

    sleep_ms(20)

display.draw_text(28, 100, "BOOT COMPLETE", GREEN)
