from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

cx = WIDTH // 2
cy = HEIGHT // 2

for x in range(0, WIDTH, 8):
    display.draw_line(cx, cy, x, 0, RED)
    display.draw_line(cx, cy, x, HEIGHT - 1, GREEN)

for y in range(0, HEIGHT, 8):
    display.draw_line(cx, cy, 0, y, BLUE)
    display.draw_line(cx, cy, WIDTH - 1, y, YELLOW)
