from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.fill_rectangle(5, 5, 30, 20, RED)

display.fill_rectangle(45, 25, 40, 30, GREEN)

display.fill_rectangle(20, 80, 70, 50, BLUE)