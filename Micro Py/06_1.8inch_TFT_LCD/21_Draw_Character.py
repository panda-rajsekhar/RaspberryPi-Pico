from st7735 import *
from colors import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_char(20, 20, 'A', WHITE)