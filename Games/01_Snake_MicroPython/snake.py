"""
JAI JAGANNATH
=========================================
Nokia-style Snake Game
=========================================

Runs on: Raspberry Pi Pico + ST7735 TFT + 4x4 Matrix Keypad

Built on top of your own drivers:
    st7735_dev.py  -> ST7735 display driver
    colors.py      -> RGB565 color constants
    keypad.py      -> 4x4 matrix keypad wiring (rows/cols/keys)

Design goals (per request):
    - Plain 2D grid movement, no animations/transitions
    - Score tracked and shown on screen
    - Responsive keypad input, independent of the game tick

Scoring / Growth:
    - Normal food is worth 1 point.
    - Every so often a "master treat" (the classic Nokia-style bonus
      item) appears at a random free cell and is worth 5 points.
      It only stays on screen for a limited time -- grab it before
      it disappears or it's gone.
    - The snake doesn't grow a full segment on every single catch.
      Instead each catch adds a small amount of "growth credit",
      and a new segment is only added once enough credit has piled
      up -- so growth feels gradual rather than one-segment-per-bite.
    - On first boot, a controls screen lists the current KEY_*
      mapping before the title screen appears.

-----------------------------------------------------------
KEYPAD KEY LAYOUT (from keypad.py's self.keys[row][col]):

        col0   col1   col2   col3
row0:   S13    S14    S15    S16
row1:   S9     S10    S11    S12
row2:   S5     S6     S7     S8
row3:   S1     S2     S3     S4

Default control mapping below forms a "+" shape using column 1
(S14/S10/S6/S2) for up/down and row 2 (S5/S6/S7) for left/right,
crossing at S6. If your physical silkscreen doesn't match this
table, just edit the six KEY_* constants below -- nothing else
in the game needs to change.
-----------------------------------------------------------
"""

from time import ticks_ms, ticks_diff, sleep_ms

from st7735_dev import ST7735, WIDTH, HEIGHT
from colors import *
from keypad import Keypad

try:
    import urandom as _rnd
except ImportError:
    import random as _rnd

# -------------------------------------------------
# Key Mapping (EDIT THESE TO MATCH YOUR KEYPAD)
# -------------------------------------------------

KEY_UP    = 'S2'
KEY_DOWN  = 'S10'
KEY_LEFT  = 'S5'
KEY_RIGHT = 'S7'
KEY_PAUSE = 'S6'
KEY_START = 'S1'   # start / restart / unpause

DIR_KEYS = {
    KEY_UP:    (0, -1),
    KEY_DOWN:  (0, 1),
    KEY_LEFT:  (-1, 0),
    KEY_RIGHT: (1, 0),
}

# -------------------------------------------------
# Game / Grid Configuration
# -------------------------------------------------

CELL = 8                 # pixels per grid cell (square snake segments)
SCORE_H = 16              # height of the score bar at the top

GRID_COLS = 15             # 15 * 8 = 120 px wide playfield
GRID_ROWS = 17             # 17 * 8 = 136 px tall playfield

FIELD_X = 4
FIELD_Y = SCORE_H + 4

TICK_MS = 180              # game speed -- lower = faster snake

# -------------------------------------------------
# Scoring / Growth Configuration
# -------------------------------------------------

NORMAL_FOOD_SCORE = 1       # points for regular food
MASTER_TREAT_SCORE = 5      # points for the bonus "master treat"

# Growth is applied gradually rather than one full segment per catch.
# Each catch adds "credit" toward the next segment; once the credit
# reaches 1.0 the snake actually grows by one cell. This keeps the
# size increase feeling like a small proportion per catch instead of
# a full segment every single time.
GROWTH_PER_NORMAL = 0.34    # ~1 extra segment every 3 normal foods
GROWTH_PER_MASTER = 0.6     # master treat contributes more credit

# The master treat shows up periodically (after every N normal foods,
# if one isn't already on screen) and disappears on its own if it
# isn't eaten in time -- just like the classic Nokia snake bonus item.
MASTER_TREAT_EVERY_N_FOOD = 4
MASTER_TREAT_DURATION_MS = 6000

try:
    MASTER_TREAT_COLOR = YELLOW
except NameError:
    try:
        MASTER_TREAT_COLOR = MAGENTA
    except NameError:
        MASTER_TREAT_COLOR = WHITE

# -------------------------------------------------
# Hardware Setup
# -------------------------------------------------

display = ST7735()
kp = Keypad()

# -------------------------------------------------
# Non-blocking Keypad Scan
# -------------------------------------------------
# kp.get_key() blocks until a key is pressed, which would freeze
# snake movement. This does one instantaneous pass over the same
# rows/cols/keys wiring and returns immediately (None if nothing
# is pressed right now).

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
    """Blocking wait used only on start/game-over screens.
    Waits for any currently-held key to release, then waits
    for a fresh press (optionally a specific key)."""

    while scan_key() is not None:
        sleep_ms(10)

    while True:
        k = scan_key()
        if k is not None and (target is None or k == target):
            return k
        sleep_ms(10)


def rand_cell_index(n):
    return _rnd.getrandbits(16) % n

# -------------------------------------------------
# Drawing Helpers
# -------------------------------------------------

def cell_to_px(col, row):
    return FIELD_X + col * CELL, FIELD_Y + row * CELL


def draw_cell(col, row, color):
    x, y = cell_to_px(col, row)
    display.fill_rectangle(x, y, CELL, CELL, color)


def draw_border():
    display.draw_rectangle(
        FIELD_X - 2,
        FIELD_Y - 2,
        GRID_COLS * CELL + 4,
        GRID_ROWS * CELL + 4,
        CYAN
    )


def draw_score():
    display.fill_rectangle(0, 0, WIDTH, SCORE_H, BLACK)
    label = "PAUSE " if paused else ""
    display.draw_text_fast(4, 4, label + "SCORE:" + str(score), WHITE, BLACK)


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

snake = []
direction = (1, 0)
pending_direction = (1, 0)
food = (0, 0)
score = 0
paused = False
game_over = False

# Master treat (bonus food) state
master_treat = None         # (col, row) or None when not on screen
master_treat_spawn = 0      # ticks_ms() timestamp of when it appeared
foods_eaten = 0             # count of normal food eaten (for spawn timing)

# Gradual-growth accumulator (see GROWTH_PER_* above)
growth_credit = 0.0


def spawn_food():
    global food
    while True:
        c = rand_cell_index(GRID_COLS)
        r = rand_cell_index(GRID_ROWS)
        if (c, r) not in snake:
            food = (c, r)
            draw_cell(c, r, RED)
            return


def spawn_master_treat():
    """Place the bonus master treat on a free cell, if one can be
    found. It will time out on its own after MASTER_TREAT_DURATION_MS
    (checked from the main loop) if the snake doesn't reach it first."""
    global master_treat, master_treat_spawn

    for _ in range(20):
        c = rand_cell_index(GRID_COLS)
        r = rand_cell_index(GRID_ROWS)
        if (c, r) not in snake and (c, r) != food:
            master_treat = (c, r)
            master_treat_spawn = ticks_ms()
            draw_cell(c, r, MASTER_TREAT_COLOR)
            return

    # Couldn't find a free cell (grid nearly full) -- just skip it
    # this time, a later call will try again.
    master_treat = None


def clear_master_treat():
    """Remove the master treat from the board (eaten or timed out)."""
    global master_treat

    if master_treat is not None:
        draw_cell(master_treat[0], master_treat[1], BLACK)
        master_treat = None


def reset_game():
    global snake, direction, pending_direction
    global score, paused, game_over
    global master_treat, foods_eaten, growth_credit

    score = 0
    paused = False
    game_over = False

    master_treat = None
    foods_eaten = 0
    growth_credit = 0.0

    mid_c = GRID_COLS // 2
    mid_r = GRID_ROWS // 2

    snake = [
        (mid_c, mid_r),
        (mid_c - 1, mid_r),
        (mid_c - 2, mid_r),
    ]
    direction = (1, 0)
    pending_direction = (1, 0)

    display.fill_screen(BLACK)
    draw_border()

    for seg in snake:
        draw_cell(seg[0], seg[1], GREEN)

    spawn_food()
    draw_score()


def step_game():
    """Advance the snake by exactly one cell. Called once per tick."""
    global snake, direction, pending_direction, score, game_over
    global master_treat, foods_eaten, growth_credit

    # Only accept the pending turn if it isn't a direct reversal
    if pending_direction != (-direction[0], -direction[1]):
        direction = pending_direction

    head_c, head_r = snake[0]
    new_head = (head_c + direction[0], head_r + direction[1])

    # Wall collision
    if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
        game_over = True
        return

    # Self collision (tail cell is fine -- it vacates this tick
    # unless we're about to eat, and food never spawns on the tail)
    if new_head in snake and new_head != snake[-1]:
        game_over = True
        return

    ate_food = (new_head == food)
    ate_master = (master_treat is not None and new_head == master_treat)

    snake.insert(0, new_head)
    draw_cell(new_head[0], new_head[1], GREEN)

    if ate_food:
        score += NORMAL_FOOD_SCORE
        foods_eaten += 1
        growth_credit += GROWTH_PER_NORMAL
        draw_score()
        spawn_food()

        # Periodically offer up a master treat, if one isn't
        # already waiting on the board.
        if master_treat is None and foods_eaten % MASTER_TREAT_EVERY_N_FOOD == 0:
            spawn_master_treat()

    elif ate_master:
        score += MASTER_TREAT_SCORE
        growth_credit += GROWTH_PER_MASTER
        draw_score()
        clear_master_treat()

    # Gradual growth: only keep the tail (i.e. actually get longer)
    # once enough growth credit has accumulated from recent catches.
    # Otherwise move normally by dropping the tail cell as usual.
    if growth_credit >= 1:
        growth_credit -= 1
    else:
        tail = snake.pop()
        draw_cell(tail[0], tail[1], BLACK)

# -------------------------------------------------
# Screens
# -------------------------------------------------

def title_screen():
    display.fill_screen(BLACK)
    display.draw_text_fast(40, 60, "SNAKE", GREEN, BLACK)
    display.draw_text_fast(16, 90, "PRESS START", WHITE, BLACK)
    wait_for_key(KEY_START)


def show_controls_screen():
    """Shown once on first boot, before the title screen, so the
    player knows which physical keys do what. Reads the mapping
    straight from the KEY_* constants, so it always matches whatever
    you've set them to -- no need to edit this function if you
    change the wiring."""

    display.fill_screen(BLACK)
    display.draw_text_fast(24, 8, "CONTROLS", CYAN, BLACK)

    rows = [
        ("UP",    KEY_UP,    WHITE),
        ("DOWN",  KEY_DOWN,  WHITE),
        ("LEFT",  KEY_LEFT,  WHITE),
        ("RIGHT", KEY_RIGHT, WHITE),
        ("PAUSE", KEY_PAUSE, MASTER_TREAT_COLOR),
        ("START", KEY_START, GREEN),
    ]

    y = 32
    for label, key_name, color in rows:
        text = label + ":" + key_name
        tx = (WIDTH - len(text) * 6) // 2
        display.draw_text_fast(tx, y, text, color, BLACK)
        y += 14

    prompt = "PRESS ANY KEY"
    px = (WIDTH - len(prompt) * 6) // 2
    display.draw_text_fast(px, y + 10, prompt, WHITE, BLACK)

    wait_for_key()


def game_over_screen():
    show_message_box(
        [
            ("GAME OVER", RED),
            ("SCORE:" + str(score), WHITE),
            ("PRESS START", CYAN),
        ]
    )
    wait_for_key(KEY_START)

# -------------------------------------------------
# Main Loop
# -------------------------------------------------

def main():
    global pending_direction, paused

    show_controls_screen()   # shown once, only on first boot
    title_screen()
    reset_game()

    last_tick = ticks_ms()
    prev_key = None

    while True:

        key = scan_key()

        # Edge-triggered: react only on the transition to a new key,
        # not every scan while a key is held down.
        if key is not None and key != prev_key:

            if key in DIR_KEYS:
                pending_direction = DIR_KEYS[key]

            elif key == KEY_PAUSE and not game_over:
                paused = not paused
                draw_score()

        prev_key = key

        # Master treat is on a real-time timer, independent of the
        # game tick, so it disappears on schedule even if the snake
        # is currently moving slowly.
        if (not paused and not game_over and master_treat is not None
                and ticks_diff(ticks_ms(), master_treat_spawn) >= MASTER_TREAT_DURATION_MS):
            clear_master_treat()

        if not paused and not game_over:
            if ticks_diff(ticks_ms(), last_tick) >= TICK_MS:
                last_tick = ticks_ms()
                step_game()

                if game_over:
                    game_over_screen()
                    reset_game()
                    last_tick = ticks_ms()
                    prev_key = None

        sleep_ms(5)


if __name__ == "__main__":
    main()