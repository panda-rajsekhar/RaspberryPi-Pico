from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.fill_triangle(64, 15, 30, 70, 98, 70, GREEN)
display.fill_triangle(64, 40, 25, 95, 103, 95, GREEN)
display.fill_triangle(64, 65, 20, 120, 108, 120, GREEN)

display.fill_rectangle(58, 120, 12, 20, BROWN)