"""
main.py -- Joystick Shield Live Status Display
Raspberry Pi Pico + ST7735 TFT (128x160, SPI0) + Funduino Joystick Shield V1.A

FILE PLACEMENT
--------------
This driver library uses flat imports ("from colors import *", etc.), so
st7735_dev.py, colors.py, fonts.py and widgets_dev.py must sit in the SAME
directory as this file on the Pico's filesystem (or in /lib) -- not nested
inside a "drivers/" subfolder the way the zip extracted them on your PC.

WIRING
------
TFT (SPI0):
  SCK  -> GP18   MOSI -> GP19   CS -> GP17   DC -> GP21   RST -> GP20
  VCC  -> 3V3(OUT)               GND -> GND

Joystick shield (as CONFIRMED working in terminal log, not as
originally commented in arb.py):
  X -> GP26 / ADC0        Y -> GP27 / ADC1
  K -> GP2   A -> GP3   B -> GP4   C -> GP9   D -> GP6   E -> GP7   F -> GP8
  NOTE: arb.py's header comment says C -> GP5, but the code (and your log,
  which shows 'C' being detected) actually uses GP9. GP5 is not used.
  Buttons are active-HIGH; internal pull-downs are enabled, idle = LOW.

RENDERING STRATEGY
-------------------
There is no framebuffer object in st7735_dev.py -- everything is a direct
SPI write. So "smooth" here means dirty-rectangle updates instead of a
full-screen clear every loop:
  - Panels, borders, and labels are drawn ONCE at startup.
  - The joystick dot is erased at its OLD position and redrawn at its NEW
    position only -- a couple of small rect writes, not the whole panel.
  - Each button cell is repainted only when THAT button's pressed state
    actually flips, not every loop.
  - The X/Y/direction text line is only rewritten when the string changes,
    and is always exactly the same width so no stale characters are left
    behind (no need to blank it first).
This keeps SPI traffic tiny and avoids the "wipe -> redraw" flicker you'd
get from calling fill_screen() every iteration.
"""

from machine import Pin, ADC
import time

from st7735_dev import ST7735
from colors import *
from widgets_dev import draw_panel

# ---------------------------------------------------------------------
# Hardware setup
# ---------------------------------------------------------------------

tft = ST7735(spi_id=0, baudrate=20_000_000, sck=18, mosi=19, cs=17, dc=21, rst=20)

x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))

buttons = {
    "K": Pin(2, Pin.IN, Pin.PULL_DOWN),
    "A": Pin(3, Pin.IN, Pin.PULL_DOWN),
    "B": Pin(4, Pin.IN, Pin.PULL_DOWN),
    "C": Pin(9, Pin.IN, Pin.PULL_DOWN),   # tested pin, see NOTE above
    "D": Pin(6, Pin.IN, Pin.PULL_DOWN),
    "E": Pin(7, Pin.IN, Pin.PULL_DOWN),
    "F": Pin(8, Pin.IN, Pin.PULL_DOWN),
}

BUTTON_ORDER = ["A", "B", "C", "D", "E", "F", "K"]

# ---------------------------------------------------------------------
# Layout constants (128 x 160 portrait screen)
# ---------------------------------------------------------------------

PANEL_BG = BLACK
PANEL_BORDER = CYAN

# --- Joystick panel -----------------------------------------------
JOY_X, JOY_Y, JOY_W, JOY_H = 4, 16, 120, 88          # bottom = 104

BOX_SIZE = 50
BOX_X = JOY_X + (JOY_W - BOX_SIZE) // 2               # 39
BOX_Y = JOY_Y + 16                                    # 32
BOX_CX = BOX_X + BOX_SIZE // 2                        # 64
BOX_CY = BOX_Y + BOX_SIZE // 2                         # 57

DOT_R = 3                                             # dot = (2*DOT_R+1) square
TRAVEL = BOX_SIZE // 2 - DOT_R - 2                    # keep dot inside border

TEXT1_Y = BOX_Y + BOX_SIZE + 4                        # X/Y readout line
TEXT2_Y = TEXT1_Y + 9                                 # direction word line

DEADZONE = 15   # ignore idle jitter -- log shows +/-1..4 counts at rest

# --- Button panel ----------------------------------------------------
BTN_X, BTN_Y, BTN_W, BTN_H = 4, 108, 120, 48          # bottom = 156
CELL_W, CELL_H, GAP = 26, 16, 3

ROW1 = ["A", "B", "C", "D"]
ROW2 = ["E", "F", "K"]


def _row_positions(names, y):
    total_w = len(names) * CELL_W + (len(names) - 1) * GAP
    start_x = BTN_X + (BTN_W - total_w) // 2
    cells = {}
    x = start_x
    for name in names:
        cells[name] = (x, y)
        x += CELL_W + GAP
    return cells


BTN_CELLS = {}
BTN_CELLS.update(_row_positions(ROW1, BTN_Y + 8))
BTN_CELLS.update(_row_positions(ROW2, BTN_Y + 8 + CELL_H + 4))

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def read_axis(adc):
    raw = adc.read_u16()
    return round((raw - 32768) / 32768 * 100)


def get_direction(x, y):
    vert = "UP" if y > DEADZONE else ("DOWN" if y < -DEADZONE else "")
    horiz = "RIGHT" if x > DEADZONE else ("LEFT" if x < -DEADZONE else "")
    if vert and horiz:
        return vert + "-" + horiz
    return vert or horiz or "CENTER"


def pad_center(s, width):
    """Manually pad/center to a FIXED width so a shorter new string fully
    overwrites a longer old one -- avoids leftover ghost characters."""
    pad = width - len(s)
    if pad <= 0:
        return s[:width]
    left = pad // 2
    return " " * left + s + " " * (pad - left)


def draw_button_cell(name, pressed):
    x, y = BTN_CELLS[name]
    fill = GREEN if pressed else BLACK
    border = CYAN if pressed else GRAY
    txt = BLACK if pressed else WHITE

    tft.fill_rectangle(x, y, CELL_W, CELL_H, fill)
    tft.draw_rectangle(x, y, CELL_W, CELL_H, border)
    tft.draw_text_fast(x + (CELL_W - 6) // 2, y + (CELL_H - 8) // 2, name, txt, fill)


def redraw_dot(cx, cy, color):
    tft.fill_rectangle(cx - DOT_R, cy - DOT_R, DOT_R * 2 + 1, DOT_R * 2 + 1, color)


def draw_static_ui():
    tft.fill_screen(BLACK)

    title = "JOYSTICK SHIELD"
    tft.draw_text_fast((128 - len(title) * 6) // 2, 2, title, WHITE, BLACK)

    draw_panel(tft, JOY_X, JOY_Y, JOY_W, JOY_H, PANEL_BORDER, title="JOYSTICK",
               title_color=WHITE, background_color=PANEL_BG)
    draw_panel(tft, BTN_X, BTN_Y, BTN_W, BTN_H, PANEL_BORDER, title="BUTTONS",
               title_color=WHITE, background_color=PANEL_BG)

    # Static travel box + center reference ticks for the joystick dot.
    # Ticks sit exactly on the crosshair lines, TRAVEL keeps the dot from
    # ever reaching them, so we never have to repair them during motion.
    tft.draw_rectangle(BOX_X, BOX_Y, BOX_SIZE, BOX_SIZE, GRAY)
    tft.draw_hline(BOX_CX - 3, BOX_CY, 7, DARKGRAY)
    tft.draw_vline(BOX_CX, BOX_CY - 3, 7, DARKGRAY)

    for name in BUTTON_ORDER:
        draw_button_cell(name, False)

    redraw_dot(BOX_CX, BOX_CY, YELLOW)

# ---------------------------------------------------------------------
# Main loop -- dirty-region updates only
# ---------------------------------------------------------------------

def main():
    draw_static_ui()

    prev_pressed = {name: False for name in BUTTON_ORDER}
    prev_dot = (BOX_CX, BOX_CY)
    prev_line1 = None
    prev_line2 = None

    while True:
        # Hardware reports the opposite of the physical tilt direction on
        # this shield -- invert both axes here so the dot, the direction
        # word, and the X/Y readout all agree with the actual push.
        x = -read_axis(x_axis)
        y = -read_axis(y_axis)

        # ---- joystick dot: move only if position actually changed ----
        dot_x = BOX_CX + int((x / 100) * TRAVEL)
        dot_y = BOX_CY - int((y / 100) * TRAVEL)   # invert Y: screen-up = up

        if (dot_x, dot_y) != prev_dot:
            redraw_dot(prev_dot[0], prev_dot[1], BLACK)
            dot_color = YELLOW if (dot_x, dot_y) == (BOX_CX, BOX_CY) else CYAN
            redraw_dot(dot_x, dot_y, dot_color)
            prev_dot = (dot_x, dot_y)

        # ---- readout text: fixed width, only rewritten when it changes ----
        line1 = "X:{:4d} Y:{:4d}".format(x, y)
        if line1 != prev_line1:
            tft.draw_text_fast(JOY_X + (JOY_W - len(line1) * 6) // 2, TEXT1_Y,
                                line1, WHITE, BLACK)
            prev_line1 = line1

        line2 = pad_center(get_direction(x, y), 12)
        if line2 != prev_line2:
            tft.draw_text_fast(JOY_X + (JOY_W - 12 * 6) // 2, TEXT2_Y,
                                line2, YELLOW, BLACK)
            prev_line2 = line2

        # ---- buttons: repaint only the ones that changed state ----
        for name in BUTTON_ORDER:
            pressed = buttons[name].value() == 1
            if pressed != prev_pressed[name]:
                draw_button_cell(name, pressed)
                prev_pressed[name] = pressed

        time.sleep_ms(40)   # ~25 Hz poll/update rate


main()

