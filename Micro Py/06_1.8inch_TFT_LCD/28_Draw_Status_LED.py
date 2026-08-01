from st7735 import *
from colors import *
from widgets import *

display = ST7735()

display.fill_screen(BLACK)

draw_panel(display,5,5,118,150,CYAN,title="STATUS LED")

draw_status_led(display,20,25,5,True,GREEN)
display.draw_text(35,21,"POWER",WHITE)

draw_status_led(display,20,45,5,False,RED)
display.draw_text(35,41,"ERROR",WHITE)

draw_status_led(display,20,65,5,True,BLUE)
display.draw_text(35,61,"USB",WHITE)

draw_status_led(display,20,85,5,True,YELLOW)
display.draw_text(35,81,"SPI",WHITE)

draw_status_led(display,20,105,5,False,CYAN)
display.draw_text(35,101,"UART",WHITE)

draw_status_led(display,20,125,5,True,MAGENTA)
display.draw_text(35,121,"I2C",WHITE)