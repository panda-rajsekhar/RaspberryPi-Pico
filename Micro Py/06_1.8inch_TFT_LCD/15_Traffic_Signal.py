from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_rectangle(35, 15, 58, 130, WHITE)

display.fill_circle(64, 40, 15, RED)
display.fill_circle(64, 80, 15, YELLOW)
display.fill_circle(64, 120, 15, GREEN)