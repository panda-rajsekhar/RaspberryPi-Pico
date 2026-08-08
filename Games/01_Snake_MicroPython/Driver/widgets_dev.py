"""
JAI JAGANNATH 
=========================================
ST7735 Widgets Library
=========================================

Author : Rajsekhar Panda

Description:
Reusable UI widgets for the ST7735 TFT
display driver.

Requires:
    st7735.py
    colors.py

Widgets:
    draw_panel()
    draw_button()
    draw_status_led()
    draw_spinner()
    ...
"""
# -------------------------------------------------
# Draw Panel
# -------------------------------------------------

def draw_panel(
    display,
    x,
    y,
    width,
    height,
    border_color,
    title=None,
    title_color=WHITE,
    background_color=BLACK
):

    # -----------------------------------------
    # Panel Background
    # -----------------------------------------

    display.fill_rectangle(
        x,
        y,
        width,
        height,
        background_color
    )

    # -----------------------------------------
    # Panel Border
    # -----------------------------------------

    display.draw_rectangle(
        x,
        y,
        width,
        height,
        border_color
    )

    # -----------------------------------------
    # Title
    # -----------------------------------------

    if title:

        tx = x + 6
        ty = y - 3

        title_width = len(title) * 6 + 4

        # Clear border behind title
        display.fill_rectangle(
            tx - 2,
            ty,
            title_width,
            8,
            background_color
        )

        # Fast text renderer
        display.draw_text_fast(
            tx,
            ty,
            title,
            title_color,
            background_color
        )
        
# -------------------------------------------------
# Draw Status LED
# -------------------------------------------------

def draw_status_led(
    display,
    x,
    y,
    radius,
    state,
    on_color=GREEN,
    off_color=DARKGRAY,
    outline_color=WHITE
):

    color = on_color if state else off_color

    display.fill_circle(
        x,
        y,
        radius,
        color
    )

    display.draw_circle(
        x,
        y,
        radius,
        outline_color
    )
        
# -------------------------------------------------
# Draw Graph
# -------------------------------------------------

def draw_graph(
    display,
    x,
    y,
    width,
    height,
    data,
    color=GREEN,
    background=BLACK,
    border=GRAY
):

    # Background
    display.fill_rectangle(
        x,
        y,
        width,
        height,
        background
    )

    # Border
    display.draw_rectangle(
        x,
        y,
        width,
        height,
        border
    )

    if len(data) < 2:
        return

    step = width / (len(data) - 1)

    previous_x = x
    previous_y = y + height - int((data[0] / 100) * (height - 2)) - 1

    for i in range(1, len(data)):

        current_x = x + int(i * step)

        current_y = (
            y
            + height
            - int((data[i] / 100) * (height - 2))
            - 1
        )

        display.draw_line(
            previous_x,
            previous_y,
            current_x,
            current_y,
            color
        )

        previous_x = current_x
        previous_y = current_y
# -------------------------------------------------
# Draw Diamond
# -------------------------------------------------

def draw_diamond(display, x, y, size, color, filled=True):

    h = size // 2

    if filled:

        for i in range(h + 1):

            display.draw_line(
                x + h - i,
                y + i,
                x + h + i,
                y + i,
                color
            )

        for i in range(h):

            display.draw_line(
                x + i + 1,
                y + h + i + 1,
                x + size - i - 2,
                y + h + i + 1,
                color
            )

    else:

        display.draw_line(x + h, y, x + size - 1, y + h, color)
        display.draw_line(x + size - 1, y + h, x + h, y + size - 1, color)
        display.draw_line(x + h, y + size - 1, x, y + h, color)
        display.draw_line(x, y + h, x + h, y, color)      
# -------------------------------------------------
# Draw Meter
# -------------------------------------------------

def draw_meter(
    display,
    x,
    y,
    value,
    maximum=100,
    segments=8,
    size=7,
    gap=1,
    filled_color=GREEN,
    empty_color=DARKGRAY
):
    """
    Draw a segmented diamond meter.

    Parameters
    ----------
    value : Current value
    maximum : Maximum possible value
    segments : Number of diamonds
    size : Diamond size (pixels)
    gap : Space between diamonds
    """

    # Clamp value
    if value < 0:
        value = 0

    if value > maximum:
        value = maximum

    # Calculate filled segments
    filled = int((value * segments) / maximum)

    cursor_x = x

    for i in range(segments):

        if i < filled:

            draw_diamond(
                display,
                cursor_x,
                y,
                size=size,
                color=filled_color,
                filled=True
            )

        else:

            draw_diamond(
                display,
                cursor_x,
                y,
                size=size,
                color=empty_color,
                filled=False
            )

        cursor_x += size + gap

# -------------------------------------------------
# Draw Button
# -------------------------------------------------

def draw_button(
    display,
    x,
    y,
    width,
    height,
    text,
    border_color=CYAN,
    fill_color=BLACK,
    text_color=WHITE,
    pressed=False
):
    """
    Draw a rectangular button.

    Parameters
    ----------
    x, y          : Top-left corner
    width, height : Button dimensions
    text          : Button label
    pressed       : True = pressed appearance
    """

    # Pressed style
    if pressed:
        fill = border_color
        border = border_color
        txt = BLACK
    else:
        fill = fill_color
        border = border_color
        txt = text_color

    # Button body
    display.fill_rectangle(
        x,
        y,
        width,
        height,
        fill
    )

    display.draw_rectangle(
        x,
        y,
        width,
        height,
        border
    )

    # -----------------------------------------
    # Center the text
    # -----------------------------------------

    char_width = 6
    char_height = 8

    text_width = len(text) * char_width

    text_x = x + (width - text_width) // 2
    text_y = y + (height - char_height) // 2

    display.draw_text(
        text_x,
        text_y,
        text,
        txt
    )

#----------------------------------------------------
#Battery
#----------------------------------------------------
def draw_battery(
    display,
    x,
    y,
    value,
    maximum=100,
    width=30,
    height=14,
    border_color=WHITE,
    fill_color=GREEN,
    empty_color=DARKGRAY
):
    """
    Draw a battery indicator.

    Parameters
    ----------
    x, y          : Top-left corner
    value         : Current battery value
    maximum       : Maximum battery value
    width,height  : Battery body size
    """

    # Clamp value
    if value < 0:
        value = 0
    if value > maximum:
        value = maximum

    # Battery terminal
    terminal_w = 3
    terminal_h = height // 3
    terminal_x = x + width
    terminal_y = y + (height - terminal_h) // 2

    # Draw battery outline
    display.draw_rectangle(
        x,
        y,
        width,
        height,
        border_color
    )

    # Draw battery terminal
    display.fill_rectangle(
        terminal_x,
        terminal_y,
        terminal_w,
        terminal_h,
        border_color
    )

    # Inner dimensions
    padding = 2

    inner_w = width - (padding * 2)
    inner_h = height - (padding * 2)

    fill_w = int(inner_w * value / maximum)

    # Draw empty area
    display.fill_rectangle(
        x + padding,
        y + padding,
        inner_w,
        inner_h,
        empty_color
    )

    # Draw charge
    if fill_w > 0:
        display.fill_rectangle(
            x + padding,
            y + padding,
            fill_w,
            inner_h,
            fill_color
        )