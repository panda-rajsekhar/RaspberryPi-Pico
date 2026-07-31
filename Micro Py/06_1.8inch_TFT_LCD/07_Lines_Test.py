from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_line(10, 10, 100, 190, RED)

display.draw_line(10, 80, 118, 80, GREEN)

display.draw_line(64, 10, 64, 150, BLUE)

display.draw_line(0, 0, WIDTH - 1, HEIGHT - 1, YELLOW)

