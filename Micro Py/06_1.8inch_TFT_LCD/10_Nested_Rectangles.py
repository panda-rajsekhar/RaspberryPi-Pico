from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

for i in range(0, 60, 5):

    display.draw_rectangle(
        i,
        i,
        WIDTH - (2 * i),
        HEIGHT - (2 * i),
        CYAN
    )