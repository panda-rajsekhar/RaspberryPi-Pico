from st7735 import *
from time import sleep

display = ST7735()

while True:
    display.fill_screen(WHITE)
    sleep(1)

    display.fill_screen(BLACK)
    sleep(1)
