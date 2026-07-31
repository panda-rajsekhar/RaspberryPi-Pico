from st7735 import *
from time import sleep

display = ST7735()

colors = [
    BLACK, WHITE, RED, GREEN,
    BLUE, YELLOW, CYAN, MAGENTA,
    ORANGE, PINK, PURPLE, GRAY,
    BROWN, NAVY
]

while True:
    for color in colors:
        display.fill_screen(color)
        sleep(0.2)      # 200 ms
