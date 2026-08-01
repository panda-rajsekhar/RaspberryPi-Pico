from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_triangle(64, 10, 10, 150, 118, 150, WHITE)

display.draw_triangle(64, 10, 37, 80, 91, 80, RED)

display.draw_triangle(37, 80, 10, 150, 64, 150, GREEN)

display.draw_triangle(91, 80, 64, 150, 118, 150, BLUE)