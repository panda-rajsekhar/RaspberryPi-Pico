from st7735 import *

display = ST7735()

display.fill_screen(BLACK)

colors = [
    RED,
    GREEN,
    BLUE,
    CYAN,
    MAGENTA,
    YELLOW,
    ORANGE,
    WHITE
]

index = 0

size = 20

for y in range(0, HEIGHT, size):

    offset = 0 if (y // size) % 2 == 0 else size // 2

    for x in range(-size + offset, WIDTH + size, size):

        color = colors[index % len(colors)]

        display.fill_triangle(
            x,
            y + size,
            x + size // 2,
            y,
            x + size,
            y + size,
            color
        )

        index += 1