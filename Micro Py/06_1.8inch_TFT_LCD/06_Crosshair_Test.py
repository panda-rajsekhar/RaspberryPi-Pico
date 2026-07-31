from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_pixel(64, 80, RED)

display.draw_pixel(63, 80, WHITE)
display.draw_pixel(65, 80, WHITE)

display.draw_pixel(64, 79, WHITE)
display.draw_pixel(64, 81, WHITE)
