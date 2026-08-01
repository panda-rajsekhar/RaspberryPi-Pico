from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_rectangle(5, 5, 30, 20, RED)

display.draw_rectangle(40, 20, 50, 40, GREEN)

display.draw_rectangle(20, 80, 90, 50, BLUE)