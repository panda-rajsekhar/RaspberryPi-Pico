from st7735 import *
from colors import *

display = ST7735()

display.fill_screen(BLACK)

display.draw_text(5, 10, "JAI JAGANNATH", WHITE)

display.draw_text(5, 25, "RASPBERRY PI", GREEN)

display.draw_text(5, 40, "PICO RP2040", CYAN)

display.draw_text(5, 55, "ST7735R TFT", YELLOW)

display.draw_text(5, 70, "MICROPYTHON", MAGENTA)

display.draw_text(
    5,
    80,
    "Raspberry Pi\nPico RP2040\n\nJAI JAGANNATH",
    CYAN
)

