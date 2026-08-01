from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_triangle(
    64, 15,
    20, 70,
    108, 70,
    RED
)

display.draw_triangle(
    64, 50,
    20, 130,
    108, 130,
    GREEN
)

display.draw_triangle(
    64, 35,
    42, 90,
    86, 90,
    CYAN
)