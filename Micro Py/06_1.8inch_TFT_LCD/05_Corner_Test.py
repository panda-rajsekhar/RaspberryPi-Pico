from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_pixel(0, 0, RED)

display.draw_pixel(WIDTH-1, 0, GREEN)

display.draw_pixel(0, HEIGHT-1, BLUE)

display.draw_pixel(WIDTH-1, HEIGHT-1, WHITE)

