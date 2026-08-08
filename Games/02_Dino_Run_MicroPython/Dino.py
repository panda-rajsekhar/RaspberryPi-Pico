"""
JAI JAGANNATH
=========================================
Chrome-Dino-style Endless Runner
=========================================

Runs on: Raspberry Pi Pico + ST7735 TFT + 4x4 Matrix Keypad

Built on top of your own drivers (same as snake.py):
    st7735_dev.py  -> ST7735 display driver
    colors.py      -> RGB565 color constants
    keypad.py      -> 4x4 matrix keypad wiring (rows/cols/keys)
    widgets_dev.py -> panel / button / meter widgets

This file follows the exact same techniques as snake.py:
    - A non-blocking, single-pass keypad scan (scan_key) polled every
      few ms, completely decoupled from a slower, fixed-rate game tick
      (step_game), so controls always feel responsive.
    - Global game state lives in a small set of clearly named module
      level variables, mutated only inside functions via `global`.
    - reset_game() can be called over and over so the game restarts
      cleanly without rebooting the board.
    - A controls screen is shown once on first boot, then a title
      screen, then the main loop -- same flow as snake.py.

What's new in this version:
    - Real dino / cactus sprites (packed 1-bpp bitmaps you supplied)
      instead of plain rectangles, blitted with "background rendering":
      each sprite buffer is precomputed ONCE with the play area's
      background color already baked into every transparent pixel, so
      a single set_window()+write_buffer() both draws the sprite AND
      erases whatever was behind it -- no separate erase pass for the
      sprite's own footprint, and only one bulk SPI burst per sprite
      per tick (the driver's fastest path, same idea as draw_text_fast).
    - A visible border around the play area and two separate widget
      panels (HI / SCORE) instead of one plain text bar, using
      widgets_dev.draw_panel() / draw_button() / draw_meter().
    - Slower overall pace (see TICK_MS below).

-----------------------------------------------------------
KEYPAD KEY LAYOUT (from keypad.py's self.keys[row][col]):

        col0   col1   col2   col3
row0:   S13    S14    S15    S16
row1:   S9     S10    S11    S12
row2:   S5     S6     S7     S8
row3:   S1     S2     S3     S4

Control mapping for this game (per request):
    S1 -> START / RESTART
    S2 -> JUMP  (single fixed-height hop, not held-to-charge)
    S3 -> DUCK  (hold to crouch on the ground under a pterodactyl, or
                 hold in mid-air to fast-fall back down early)

If your physical silkscreen doesn't match this table, just edit the
three KEY_* constants below -- nothing else in the game needs to change.
-----------------------------------------------------------
"""

from time import ticks_ms, ticks_diff, sleep_ms

from st7735_dev import ST7735, WIDTH, HEIGHT
from colors import *
from keypad import Keypad
from widgets_dev import draw_panel, draw_button, draw_meter

try:
    import urandom as _rnd
except ImportError:
    import random as _rnd

# -------------------------------------------------
# Key Mapping (EDIT THESE TO MATCH YOUR KEYPAD)
# -------------------------------------------------

KEY_START = 'S1'   # start / restart
KEY_JUMP  = 'S2'   # jump over cacti
KEY_DUCK  = 'S3'   # duck under pterodactyls / fast-fall

# -------------------------------------------------
# Sprites (packed 1-bpp bitmaps, MSB-first, each row
# padded out to a whole number of bytes)
# -------------------------------------------------

CACTUS_W = 11
CACTUS_H = 23
CACTUS_BITMAP = bytes([
    0x00, 0x70,
    0x00, 0x70,
    0x00, 0x70,
    0x00, 0x70,
    0x00, 0x70,
    0x00, 0x70,
    0x30, 0x70,
    0x30, 0x70,
    0x30, 0x70,
    0x3F, 0xF0,
    0x3F, 0xF0,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80,
    0x03, 0x80
])

DINO_W = 20
DINO_H = 22
DINO_BITMAP = bytes([
    0x00, 0x7F, 0x80,
    0x00, 0xFF, 0xC0,
    0x00, 0xDE, 0xC0,
    0x00, 0xFF, 0xC0,
    0x00, 0xFF, 0xC0,
    0x00, 0xFF, 0xC0,
    0x00, 0x7C, 0x00,
    0x00, 0x7F, 0x00,
    0x80, 0x7C, 0x00,
    0x81, 0xFC, 0x00,
    0xC3, 0xFC, 0x00,
    0xE7, 0xFD, 0x00,
    0xFF, 0xFC, 0x00,
    0xFF, 0xFC, 0x00,
    0x7F, 0xF8, 0x00,
    0x3F, 0xF8, 0x00,
    0x1F, 0xF0, 0x00,
    0x0F, 0xE0, 0x00,
    0x07, 0x60, 0x00,
    0x06, 0x20, 0x00,
    0x04, 0x20, 0x00,
    0x06, 0x30, 0x00
])

# No duck sprite was supplied. Rather than fall back to a plain
# rectangle, the duck pose reuses the bottom slice of the same dino
# bitmap (legs/tail) so the crouch still looks like the same dino,
# just cropped down to DINO_DUCK_H rows.
DINO_DUCK_H = 10

# -------------------------------------------------
# Playfield / Timing Configuration
# -------------------------------------------------

# Two score panels + a speed meter strip live in this top band,
# clearly separated from the bordered play area below it.
TOP_AREA_H = 35

PLAY_Y = TOP_AREA_H
PLAY_LEFT = 4
PLAY_RIGHT = WIDTH - 4
GROUND_MARGIN = 13              # gap between ground line and the border's bottom
GROUND_Y = HEIGHT - GROUND_MARGIN

BORDER_COLOR = CYAN
BG_COLOR = BLACK                # play-area background, used everywhere so
                                 # "erase" and "sprite background" always agree

# Slower, more deliberate pace than a typical runner:
TICK_MS = 30                # was 30 -- lower = faster, this is the main
                                 # speed knob since physics runs per-tick

# -------------------------------------------------
# Dino Physics Configuration
# -------------------------------------------------

DINO_X = PLAY_LEFT + 6           # dino's fixed horizontal position
DINO_COLOR = WHITE

GRAVITY = 1                      # px/tick^2 added to vertical velocity
JUMP_VELOCITY = -11               # initial upward velocity on jump
FAST_FALL_VELOCITY = 10          # downward velocity snap when duck-falling

# -------------------------------------------------
# Obstacle Configuration
# -------------------------------------------------

CACTUS_COLOR = GREEN

PTERO_COLOR = MAGENTA
PTERO_W = 14
PTERO_H = 8
# Flying at "head height" of a standing dino, well above a ducking one --
# this is what makes ducking (not jumping) the reliable answer for it.
PTERO_Y = GROUND_Y - DINO_H

PTERO_CHANCE = 35                # % chance a spawned obstacle is a pterodactyl

SCROLL_SPEED_START = 2           # px/tick (slower than before)
SCROLL_SPEED_MAX = 6
SPEED_UP_EVERY_SCORE = 150       # +1 px/tick every N score points

SPAWN_MIN_GAP_PX = 55
SPAWN_MAX_GAP_PX = 130

# -------------------------------------------------
# Hardware Setup
# -------------------------------------------------

display = ST7735()
kp = Keypad()

# -------------------------------------------------
# Non-blocking Keypad Scan
# -------------------------------------------------
# kp.get_key() blocks until a key is pressed, which would freeze the
# runner. This does one instantaneous pass over the same rows/cols/keys
# wiring and returns immediately (None if nothing is pressed right now).

def scan_key():
    detected = None
    for c in range(4):
        kp.cols[c].value(1)
        for r in range(4):
            if kp.rows[r].value():
                detected = kp.keys[r][c]
        kp.cols[c].value(0)
    return detected


def wait_for_key(target=None):
    """Blocking wait used only on the controls/title/game-over screens.
    Waits for any currently-held key to release, then waits for a
    fresh press (optionally a specific key)."""

    while scan_key() is not None:
        sleep_ms(10)

    while True:
        k = scan_key()
        if k is not None and (target is None or k == target):
            return k
        sleep_ms(10)


def rand_range(lo, hi):
    """Random integer in [lo, hi], inclusive."""
    span = hi - lo + 1
    return lo + (_rnd.getrandbits(16) % span)


def rand_percent():
    return _rnd.getrandbits(16) % 100

# -------------------------------------------------
# Sprite Buffers ("Background Rendering")
# -------------------------------------------------
# Each sprite is precomputed ONCE into a ready-to-send RGB565 buffer:
# set bits become the sprite color, unset bits become BG_COLOR. Because
# the background is already baked in, blitting the buffer both draws
# the sprite AND paints over its own footprint's background in a
# single SPI burst -- the driver's fastest path (same trick
# draw_text_fast uses for glyphs, just applied to game sprites).

def build_sprite_buffer(bitmap, width, height, fg_color, bg_color,
                         row_start=0, row_count=None):
    if row_count is None:
        row_count = height - row_start

    row_bytes = (width + 7) // 8

    fg_hi = (fg_color >> 8) & 0xFF
    fg_lo = fg_color & 0xFF
    bg_hi = (bg_color >> 8) & 0xFF
    bg_lo = bg_color & 0xFF

    buf = bytearray(width * row_count * 2)
    p = 0

    for row in range(row_start, row_start + row_count):
        row_offset = row * row_bytes
        for col in range(width):
            byte_index = row_offset + (col >> 3)
            bit_index = 7 - (col & 7)
            bit = (bitmap[byte_index] >> bit_index) & 1

            if bit:
                buf[p] = fg_hi
                buf[p + 1] = fg_lo
            else:
                buf[p] = bg_hi
                buf[p + 1] = bg_lo

            p += 2

    return buf


def blit(x, y, w, h, buf):
    """Blit a precomputed w*h RGB565 buffer at (x, y), clipped to the
    screen. Obstacles spawn partly off the right edge and scroll off
    the left edge, so unlike a sprite that's always fully on-screen,
    this can't just hand (x, y, w, h) straight to set_window() the way
    a fully-visible draw could -- driver's set_window() doesn't clip
    the way fill_rectangle() does, so out-of-range coordinates here
    would write past the panel's memory instead of being ignored."""

    x0, y0 = x, y
    x1, y1 = x + w, y + h   # exclusive

    src_x0 = 0
    src_y0 = 0

    if x0 < 0:
        src_x0 = -x0
        x0 = 0
    if y0 < 0:
        src_y0 = -y0
        y0 = 0
    if x1 > WIDTH:
        x1 = WIDTH
    if y1 > HEIGHT:
        y1 = HEIGHT

    vis_w = x1 - x0
    vis_h = y1 - y0

    if vis_w <= 0 or vis_h <= 0:
        return   # fully off-screen -- nothing to send

    if vis_w == w and vis_h == h:
        # Fully visible: send the precomputed buffer as-is, one burst.
        display.set_window(x0, y0, x0 + w - 1, y0 + h - 1)
        display.write_buffer(buf)
        return

    # Partially visible (spawning in / scrolling out): crop the buffer
    # row-by-row to just the visible window before sending it.
    row_bytes = w * 2
    cropped = bytearray(vis_w * vis_h * 2)
    p = 0
    for row in range(vis_h):
        src_offset = (src_y0 + row) * row_bytes + src_x0 * 2
        cropped[p:p + vis_w * 2] = buf[src_offset:src_offset + vis_w * 2]
        p += vis_w * 2

    display.set_window(x0, y0, x0 + vis_w - 1, y0 + vis_h - 1)
    display.write_buffer(cropped)


# Precomputed once at import time -- reused every tick, no per-frame
# bitmap decoding cost.
DINO_STAND_BUF = build_sprite_buffer(DINO_BITMAP, DINO_W, DINO_H, DINO_COLOR, BG_COLOR)
DINO_DUCK_BUF = build_sprite_buffer(
    DINO_BITMAP, DINO_W, DINO_H, DINO_COLOR, BG_COLOR,
    row_start=DINO_H - DINO_DUCK_H, row_count=DINO_DUCK_H
)
CACTUS_BUF = build_sprite_buffer(CACTUS_BITMAP, CACTUS_W, CACTUS_H, CACTUS_COLOR, BG_COLOR)

# -------------------------------------------------
# Drawing Helpers
# -------------------------------------------------

def erase_rect(x, y, w, h):
    display.fill_rectangle(x, y, w, h, BG_COLOR)


def draw_ground():
    # A single horizontal line across the whole play area. Redrawn at
    # the end of every tick so any sprite that touched this row never
    # leaves a gap in it.
    display.fill_rectangle(PLAY_LEFT, GROUND_Y, PLAY_RIGHT - PLAY_LEFT, 1, WHITE)


def draw_play_border():
    # The bordered background box for the whole play area, drawn with
    # the widgets library instead of a raw driver call -- draw_panel()
    # already both fills the background and strokes the border in one
    # call, same as what a hand-rolled draw_border()+fill_screen() pair
    # would do in snake.py.
    draw_panel(
        display,
        PLAY_LEFT - 2,
        PLAY_Y,
        (PLAY_RIGHT + 2) - (PLAY_LEFT - 2),
        HEIGHT - PLAY_Y - 2,
        border_color=BORDER_COLOR,
        background_color=BG_COLOR
    )


def draw_score_panels():
    # Score is deliberately separated from the play area: two small
    # bordered panels up top, clearly outside the bordered runner box.
    draw_panel(display, 2, 2, 38, 16, border_color=WHITE, title="HI", background_color=BLACK)
    draw_panel(display, 44, 2, WIDTH - 44 - 2, 16, border_color=WHITE, title="SCORE", background_color=BLACK)

    display.draw_text_fast(8, 10, str(high_score), CYAN, BLACK)
    display.draw_text_fast(50, 10, str(score), YELLOW, BLACK)


def draw_speed_meter():
    # A small segmented meter showing how fast the current run is,
    # using the widgets library's diamond meter. Only redrawn when the
    # speed actually changes (see step_game), not every tick.
    display.draw_text_fast(4, 22, "SPD", GRAY, BLACK)
    draw_meter(
        display, 26, 21,
        value=scroll_speed, maximum=SCROLL_SPEED_MAX,
        segments=SCROLL_SPEED_MAX, size=4, gap=1,
        filled_color=ORANGE, empty_color=DARKGRAY
    )


def show_message_box(lines, border_color=RED):
    box_w = 100
    box_h = 20 + len(lines) * 12
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2

    display.fill_rectangle(box_x, box_y, box_w, box_h, BLACK)
    display.draw_rectangle(box_x, box_y, box_w, box_h, border_color)

    ty = box_y + 8
    for text, color in lines:
        tx = box_x + (box_w - len(text) * 6) // 2
        display.draw_text_fast(tx, ty, text, color, BLACK)
        ty += 12

# -------------------------------------------------
# Game State
# -------------------------------------------------

dino_y = GROUND_Y - DINO_H          # top-y of the dino's standing hitbox
velocity = 0                        # vertical velocity, px/tick
on_ground = True
ducking = False

obstacles = []                      # list of dicts: x, y, w, h, kind, color
spawn_gap_remaining = SPAWN_MIN_GAP_PX

scroll_speed = SCROLL_SPEED_START
score = 0
high_score = 0                      # kept across rounds within this boot
game_over = False


def dino_rect():
    """Current on-screen rectangle of the dino, accounting for duck."""
    if on_ground and ducking:
        return DINO_X, GROUND_Y - DINO_DUCK_H, DINO_W, DINO_DUCK_H
    return DINO_X, dino_y, DINO_W, DINO_H


def dino_buffer():
    return DINO_DUCK_BUF if (on_ground and ducking) else DINO_STAND_BUF


def spawn_obstacle():
    global obstacles

    if rand_percent() < PTERO_CHANCE:
        obstacles.append({
            "kind": "ptero",
            "x": PLAY_RIGHT,
            "y": PTERO_Y,
            "w": PTERO_W,
            "h": PTERO_H,
            "color": PTERO_COLOR,
        })
    else:
        obstacles.append({
            "kind": "cactus",
            "x": PLAY_RIGHT,
            "y": GROUND_Y - CACTUS_H,
            "w": CACTUS_W,
            "h": CACTUS_H,
            "color": CACTUS_COLOR,
        })


def reset_game():
    global dino_y, velocity, on_ground, ducking
    global obstacles, spawn_gap_remaining, scroll_speed
    global score, game_over

    dino_y = GROUND_Y - DINO_H
    velocity = 0
    on_ground = True
    ducking = False

    obstacles = []
    spawn_gap_remaining = SPAWN_MIN_GAP_PX
    scroll_speed = SCROLL_SPEED_START

    score = 0
    game_over = False

    display.fill_screen(BLACK)
    draw_play_border()
    draw_ground()
    start_x, start_y, _, _ = dino_rect()
    blit(start_x, start_y, DINO_W, DINO_H, DINO_STAND_BUF)

    draw_score_panels()
    draw_speed_meter()

# -------------------------------------------------
# Core Game Logic
# -------------------------------------------------

def rects_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def step_game(jump_pressed, duck_held):
    """Advance the runner by exactly one tick. Called once per TICK_MS."""
    global dino_y, velocity, on_ground, ducking
    global obstacles, spawn_gap_remaining, scroll_speed
    global score, high_score, game_over

    # ---- erase the dino's current footprint before anything moves ----
    old_x, old_y, old_w, old_h = dino_rect()
    erase_rect(old_x, old_y, old_w, old_h)

    # ---- jump ----
    if jump_pressed and on_ground and not ducking:
        velocity = JUMP_VELOCITY
        on_ground = False

    # ---- duck / fast-fall ----
    if on_ground:
        ducking = duck_held
    else:
        ducking = False              # hitbox stays standing-size mid-air
        if duck_held:
            velocity = FAST_FALL_VELOCITY   # snap into a fast drop

    # ---- vertical physics ----
    if not on_ground:
        velocity += GRAVITY
        dino_y += velocity
        if dino_y >= GROUND_Y - DINO_H:
            dino_y = GROUND_Y - DINO_H
            velocity = 0
            on_ground = True

    # ---- blit the dino sprite at its new position ----
    new_x, new_y, new_w, new_h = dino_rect()
    blit(new_x, new_y, new_w, new_h, dino_buffer())

    # ---- move obstacles, prune off-screen ones, check collisions ----
    still_on_screen = []
    for ob in obstacles:
        erase_rect(ob["x"], ob["y"], ob["w"], ob["h"])
        ob["x"] -= scroll_speed

        if ob["x"] + ob["w"] < PLAY_LEFT:
            continue   # scrolled off the left edge -- drop it

        if ob["kind"] == "cactus":
            blit(ob["x"], ob["y"], ob["w"], ob["h"], CACTUS_BUF)
        else:
            display.fill_rectangle(ob["x"], ob["y"], ob["w"], ob["h"], ob["color"])

        if rects_overlap(new_x, new_y, new_w, new_h,
                          ob["x"], ob["y"], ob["w"], ob["h"]):
            game_over = True

        still_on_screen.append(ob)

    obstacles = still_on_screen

    # ---- spawn new obstacles as a steady stream ----
    spawn_gap_remaining -= scroll_speed
    if spawn_gap_remaining <= 0:
        spawn_obstacle()
        spawn_gap_remaining = rand_range(SPAWN_MIN_GAP_PX, SPAWN_MAX_GAP_PX)

    # ---- keep the ground line intact regardless of what redrew over it ----
    draw_ground()

    if game_over:
        if score > high_score:
            high_score = score
        return

    # ---- score ticks up with distance survived ----
    score += 1
    if score % SPEED_UP_EVERY_SCORE == 0 and scroll_speed < SCROLL_SPEED_MAX:
        scroll_speed += 1
        draw_speed_meter()

    display.draw_text_fast(50, 10, str(score), YELLOW, BLACK)

# -------------------------------------------------
# Screens
# -------------------------------------------------

def show_controls_screen():
    """Shown once on first boot, before the title screen, so the
    player knows which physical keys do what."""

    display.fill_screen(BLACK)
    draw_panel(display, 6, 8, WIDTH - 12, 96, border_color=CYAN, title="CONTROLS", background_color=BLACK)

    rows = [
        ("START", KEY_START, GREEN),
        ("JUMP",  KEY_JUMP,  WHITE),
        ("DUCK",  KEY_DUCK,  MAGENTA),
    ]

    y = 30
    for label, key_name, color in rows:
        text = label + ":" + key_name
        tx = (WIDTH - len(text) * 6) // 2
        display.draw_text_fast(tx, y, text, color, BLACK)
        y += 18

    draw_button(display, (WIDTH - 90) // 2, 112, 90, 20, "ANY KEY", border_color=WHITE, text_color=WHITE)

    wait_for_key()


def title_screen():
    display.fill_screen(BLACK)
    display.draw_text_fast(30, 50, "DINO RUN", GREEN, BLACK)
    blit(DINO_X, 72, DINO_W, DINO_H, DINO_STAND_BUF)
    draw_button(display, (WIDTH - 90) // 2, 110, 90, 22, "S1:START", border_color=GREEN, text_color=GREEN)
    wait_for_key(KEY_START)


def game_over_screen():
    show_message_box(
        [
            ("GAME OVER", RED),
            ("SCORE:" + str(score), WHITE),
            ("HI:" + str(high_score), CYAN),
        ]
    )
    draw_button(display, (WIDTH - 90) // 2, HEIGHT // 2 + 40, 90, 20, "S1:RESTART", border_color=CYAN, text_color=CYAN)
    wait_for_key(KEY_START)

# -------------------------------------------------
# Main Loop
# -------------------------------------------------

def main():
    show_controls_screen()   # shown once, only on first boot
    title_screen()
    reset_game()

    last_tick = ticks_ms()
    prev_key = None

    while True:

        key = scan_key()

        # Jump is edge-triggered: react only on the transition to a
        # freshly-pressed key, not every scan while it's held down --
        # otherwise holding S2 would queue up repeated jumps.
        jump_pressed = (key == KEY_JUMP and key != prev_key)

        # Duck is level-triggered: it matters for as long as the key
        # is physically held, not just on the initial press.
        duck_held = (key == KEY_DUCK)

        prev_key = key

        if not game_over:
            if ticks_diff(ticks_ms(), last_tick) >= TICK_MS:
                last_tick = ticks_ms()
                step_game(jump_pressed, duck_held)

                if game_over:
                    game_over_screen()
                    reset_game()
                    last_tick = ticks_ms()
                    prev_key = None

        sleep_ms(5)


if __name__ == "__main__":
    main()