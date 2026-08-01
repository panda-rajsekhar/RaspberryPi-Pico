from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.fill_circle(32, 40, 18, RED)
display.fill_circle(96, 40, 18, GREEN)
display.fill_circle(64, 100, 28, BLUE)