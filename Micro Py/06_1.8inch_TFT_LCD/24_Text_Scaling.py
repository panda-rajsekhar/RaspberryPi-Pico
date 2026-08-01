from st7735 import *
from colors import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_text(5, 5, "1X", WHITE, 1)

display.draw_text(5, 20, "2X", GREEN, 2)

display.draw_text(5, 50, "3X", CYAN, 3)