from st7735 import *
from colors import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_text(10, 10, "WHITE", WHITE)
display.draw_text(10, 22, "RED", RED)
display.draw_text(10, 34, "GREEN", GREEN)
display.draw_text(10, 46, "BLUE", BLUE)
display.draw_text(10, 58, "YELLOW", YELLOW)
display.draw_text(10, 70, "CYAN", CYAN)
display.draw_text(10, 82, "MAGENTA", MAGENTA)
display.draw_text(10, 94, "ORANGE", ORANGE)
display.draw_text(10, 106, "NAVY", NAVY)
display.draw_text(10, 118, "GRAY", GRAY)
display.draw_text(10, 130, "BROWN", BROWN)
display.draw_text(10, 142, "PINK", PINK)