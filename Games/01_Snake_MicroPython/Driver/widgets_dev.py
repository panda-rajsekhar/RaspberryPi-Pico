"""
JAI JAGANNATH
=========================================
ST7735 Widgets Library
=========================================

Author : Rajsekhar Panda

Reusable UI widgets for the ST7735 TFT display driver.

Requires:
    st7735_dev.py
    colors.py

Widgets:
    draw_panel()
    draw_status_led()
    draw_graph()
    draw_diamond()
    draw_meter()
    draw_button()
    draw_battery()
"""

from colors import *


# -------------------------------------------------
# Draw Panel
# -------------------------------------------------

def draw_panel(display, x, y, width, height, border_color,
               title=None, title_color=WHITE, background_color=BLACK):

    display.fill_rectangle(x, y, width, height, background_color)
    display.draw_rectangle(x, y, width, height, border_color)

    if title:
        tx, ty = x + 6, y - 3
        title_width = len(title) * 6 + 4

        # Clear the border behind the title so it reads cleanly
        display.fill_rectangle(tx - 2, ty, title_width, 8, background_color)
        display.draw_text_fast(tx, ty, title, title_color, background_color)


# -------------------------------------------------
# Draw Status LED
# -------------------------------------------------

def draw_status_led(display, x, y, radius, state,
                     on_color=GREEN, off_color=DARKGRAY, outline_color=WHITE):

    color = on_color if state else off_color

    display.fill_circle(x, y, radius, color)
    display.draw_circle(x, y, radius, outline_color)


# -------------------------------------------------
# Draw Graph
# -------------------------------------------------

def draw_graph(display, x, y, width, height, data,
                color=GREEN, background=BLACK, border=GRAY):

    display.fill_rectangle(x, y, width, height, background)
    display.draw_rectangle(x, y, width, height, border)

    if len(data) < 2:
        return

    step = width / (len(data) - 1)
    prev_x = x
    prev_y = y + height - int((data[0] / 100) * (height - 2)) - 1

    for i in range(1, len(data)):
        cur_x = x + int(i * step)
        cur_y = y + height - int((data[i] / 100) * (height - 2)) - 1

        display.draw_line(prev_x, prev_y, cur_x, cur_y, color)
        prev_x, prev_y = cur_x, cur_y


# -------------------------------------------------
# Draw Diamond
# -------------------------------------------------

def draw_diamond(display, x, y, size, color, filled=True):

    h = size // 2

    if filled:
        for i in range(h + 1):
            display.draw_line(x + h - i, y + i, x + h + i, y + i, color)

        for i in range(h):
            display.draw_line(x + i + 1, y + h + i + 1,
                               x + size - i - 2, y + h + i + 1, color)
    else:
        display.draw_line(x + h, y, x + size - 1, y + h, color)
        display.draw_line(x + size - 1, y + h, x + h, y + size - 1, color)
        display.draw_line(x + h, y + size - 1, x, y + h, color)
        display.draw_line(x, y + h, x + h, y, color)


# -------------------------------------------------
# Draw Meter (segmented diamond meter)
# -------------------------------------------------

def draw_meter(display, x, y, value, maximum=100, segments=8, size=7, gap=1,
                filled_color=GREEN, empty_color=DARKGRAY):
    """
    value    : current value
    maximum  : maximum possible value
    segments : number of diamonds
    size     : diamond size (pixels)
    gap      : space between diamonds
    """

    value = max(0, min(value, maximum))
    filled = int((value * segments) / maximum)

    cursor_x = x
    for i in range(segments):
        color = filled_color if i < filled else empty_color
        draw_diamond(display, cursor_x, y, size=size, color=color, filled=(i < filled))
        cursor_x += size + gap


# -------------------------------------------------
# Draw Button
# -------------------------------------------------

def draw_button(display, x, y, width, height, text,
                 border_color=CYAN, fill_color=BLACK, text_color=WHITE, pressed=False):
    """
    x, y          : top-left corner
    width, height : button dimensions
    text          : button label
    pressed       : True = pressed appearance (filled with border_color)
    """

    if pressed:
        fill, border, txt = border_color, border_color, BLACK
    else:
        fill, border, txt = fill_color, border_color, text_color

    display.fill_rectangle(x, y, width, height, fill)
    display.draw_rectangle(x, y, width, height, border)

    char_width, char_height = 6, 8
    text_x = x + (width - len(text) * char_width) // 2
    text_y = y + (height - char_height) // 2

    display.draw_text(text_x, text_y, text, txt)


# -------------------------------------------------
# Draw Battery
# -------------------------------------------------

def draw_battery(display, x, y, value, maximum=100, width=30, height=14,
                  border_color=WHITE, fill_color=GREEN, empty_color=DARKGRAY):
    """
    x, y         : top-left corner
    value        : current battery value
    maximum      : maximum battery value
    width,height : battery body size
    """

    value = max(0, min(value, maximum))

    terminal_w = 3
    terminal_h = height // 3
    terminal_x = x + width
    terminal_y = y + (height - terminal_h) // 2

    display.draw_rectangle(x, y, width, height, border_color)
    display.fill_rectangle(terminal_x, terminal_y, terminal_w, terminal_h, border_color)

    padding = 2
    inner_w = width - (padding * 2)
    inner_h = height - (padding * 2)
    fill_w = int(inner_w * value / maximum)

    display.fill_rectangle(x + padding, y + padding, inner_w, inner_h, empty_color)

    if fill_w > 0:
        display.fill_rectangle(x + padding, y + padding, fill_w, inner_h, fill_color)
