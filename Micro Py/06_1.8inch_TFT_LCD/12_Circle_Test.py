from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_circle(64, 80, 15, RED)
display.draw_circle(64, 80, 30, GREEN)
display.draw_circle(64, 80, 45, BLUE)
display.draw_circle(64, 80, 60, YELLOW)