from st7735 import *

display = ST7735()

display.fill_screen(WHITE)

from st7735 import *

display = ST7735()

display.fill_screen(WHITE)

r = 16

# Left Column
display.draw_circle(46, 44, r, BLUE)
display.draw_circle(46, 80, r, BLACK)
display.draw_circle(46, 116, r, RED)

# Right Column (offset)
display.draw_circle(74, 62, r, YELLOW)
display.draw_circle(74, 98, r, GREEN)