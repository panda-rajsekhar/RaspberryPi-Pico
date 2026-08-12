from machine import Pin, ADC
import time
import random

from st7735_dev import ST7735
from colors import *
from widgets_dev import draw_panel


# ============================================================
# HARDWARE
# ============================================================

tft = ST7735(
    spi_id=0,
    baudrate=20_000_000,
    sck=18,
    mosi=19,
    cs=17,
    dc=21,
    rst=20
)

x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))

btn_rotate = Pin(3, Pin.IN, Pin.PULL_DOWN)   # A
btn_drop   = Pin(4, Pin.IN, Pin.PULL_DOWN)   # B
btn_pause  = Pin(2, Pin.IN, Pin.PULL_DOWN)   # K


# ============================================================
# SCREEN / BOARD
# ============================================================

COLS = 8
ROWS = 16
CELL = 8

BOARD_X = 4
BOARD_Y = 18

BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL

SIDE_X = 76

# NEXT box
NEXT_BOX_X = 76
NEXT_BOX_Y = 28
NEXT_BOX_W = 32
NEXT_BOX_H = 32

# "NEXT" will be ABOVE the box
NEXT_TEXT_X = NEXT_BOX_X
NEXT_TEXT_Y = 18


# ============================================================
# GAME SPEED
# ============================================================

GRAVITY = 600
SOFT_DROP = 80
MOVE_REPEAT = 150   # ms between left/right moves while joystick held


# ============================================================
# PIECES
# ============================================================

SHAPES = {

    "I": [
        [(0,1),(1,1),(2,1),(3,1)],
        [(2,0),(2,1),(2,2),(2,3)]
    ],

    "O": [
        [(1,0),(2,0),(1,1),(2,1)]
    ],

    "T": [
        [(1,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(2,1),(1,2)],
        [(1,0),(0,1),(1,1),(1,2)]
    ],

    "S": [
        [(1,0),(2,0),(0,1),(1,1)],
        [(1,0),(1,1),(2,1),(2,2)]
    ],

    "Z": [
        [(0,0),(1,0),(1,1),(2,1)],
        [(2,0),(1,1),(2,1),(1,2)]
    ],

    "J": [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,2)],
        [(1,0),(1,1),(1,2),(0,2)]
    ],

    "L": [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,1),(1,1),(2,1),(0,2)],
        [(0,0),(1,0),(1,1),(1,2)]
    ]
}


COLORS = {
    "I": CYAN,
    "O": YELLOW,
    "T": PURPLE,
    "S": GREEN,
    "Z": RED,
    "J": BLUE,
    "L": ORANGE
}


PIECE_TYPES = ["I", "O", "T", "S", "Z", "J", "L"]


# ============================================================
# GAME STATE
# ============================================================

board = [[None for x in range(COLS)] for y in range(ROWS)]

piece_type = None
piece_rotation = 0
piece_x = 2
piece_y = 0

next_piece = None

score = 0
level = 1
lines = 0

paused = False
game_over = False


# ============================================================
# JOYSTICK
# ============================================================

def joystick(adc):

    value = adc.read_u16()

    # Convert 0-65535 to approximately -100 to +100
    value = (value - 32768) * 100 // 32768

    return -value


# ============================================================
# PIECE HELPERS
# ============================================================

def get_shape():

    return SHAPES[piece_type][piece_rotation]


def random_piece():

    return random.choice(PIECE_TYPES)


# ============================================================
# COLLISION
# ============================================================

def collision(x, y, rotation):

    shape = SHAPES[piece_type][rotation]

    for cx, cy in shape:

        col = x + cx
        row = y + cy

        # Left / right walls
        if col < 0 or col >= COLS:
            return True

        # Bottom
        if row >= ROWS:
            return True

        # Existing block
        if row >= 0:
            if board[row][col] is not None:
                return True

    return False


# ============================================================
# DRAW BOARD CELL
# ============================================================

def draw_cell(col, row, color):

    if row < 0:
        return

    x = BOARD_X + col * CELL
    y = BOARD_Y + row * CELL

    tft.fill_rectangle(
        x,
        y,
        CELL - 1,
        CELL - 1,
        color
    )


# ============================================================
# DRAW CURRENT PIECE
# ============================================================

def draw_piece():

    color = COLORS[piece_type]

    for cx, cy in get_shape():

        draw_cell(
            piece_x + cx,
            piece_y + cy,
            color
        )


def erase_piece():

    for cx, cy in get_shape():

        col = piece_x + cx
        row = piece_y + cy

        if 0 <= row < ROWS and 0 <= col < COLS:

            color = board[row][col]

            if color is None:
                color = BLACK

            draw_cell(col, row, color)


# ============================================================
# DRAW ENTIRE BOARD
# ============================================================

def draw_board():

    for row in range(ROWS):

        for col in range(COLS):

            color = board[row][col]

            if color is None:
                color = BLACK

            draw_cell(col, row, color)


# ============================================================
# NEXT PIECE
# ============================================================

def draw_next():

    # Clear box
    tft.fill_rectangle(
        NEXT_BOX_X + 1,
        NEXT_BOX_Y + 1,
        NEXT_BOX_W - 2,
        NEXT_BOX_H - 2,
        BLACK
    )

    shape = SHAPES[next_piece][0]
    color = COLORS[next_piece]

    for cx, cy in shape:

        x = NEXT_BOX_X + 5 + cx * 6
        y = NEXT_BOX_Y + 5 + cy * 6

        tft.fill_rectangle(
            x,
            y,
            5,
            5,
            color
        )


# ============================================================
# UI
# ============================================================

def draw_ui():

    tft.fill_screen(BLACK)

    # Title
    tft.draw_text_fast(
        48,
        2,
        "TETRIS",
        WHITE,
        BLACK
    )

    # Board
    draw_panel(
        tft,
        BOARD_X - 2,
        BOARD_Y - 2,
        BOARD_W + 4,
        BOARD_H + 4,
        GRAY,
        background_color=BLACK
    )

    # --------------------------------------------------------
    # NEXT LABEL
    # --------------------------------------------------------

    # IMPORTANT:
    # NEXT is ABOVE the box, not inside it.
    tft.draw_text_fast(
        NEXT_TEXT_X,
        NEXT_TEXT_Y,
        "NEXT",
        WHITE,
        BLACK
    )

    # Next box
    draw_panel(
        tft,
        NEXT_BOX_X,
        NEXT_BOX_Y,
        NEXT_BOX_W,
        NEXT_BOX_H,
        GRAY,
        background_color=BLACK
    )

    # Score
    tft.draw_text_fast(
        SIDE_X,
        68,
        "SCORE",
        WHITE,
        BLACK
    )

    tft.draw_text_fast(
        SIDE_X,
        78,
        str(score),
        YELLOW,
        BLACK
    )

    # Level
    tft.draw_text_fast(
        SIDE_X,
        96,
        "LEVEL",
        WHITE,
        BLACK
    )

    tft.draw_text_fast(
        SIDE_X,
        106,
        str(level),
        YELLOW,
        BLACK
    )

    # Lines
    tft.draw_text_fast(
        SIDE_X,
        124,
        "LINES",
        WHITE,
        BLACK
    )

    tft.draw_text_fast(
        SIDE_X,
        134,
        str(lines),
        YELLOW,
        BLACK
    )

    draw_board()


# ============================================================
# SPAWN PIECE
# ============================================================

def spawn_piece():

    global piece_type
    global piece_rotation
    global piece_x
    global piece_y
    global next_piece
    global game_over

    piece_type = next_piece

    if piece_type is None:
        piece_type = random_piece()

    next_piece = random_piece()

    piece_rotation = 0
    piece_x = 2
    piece_y = 0

    if collision(piece_x, piece_y, piece_rotation):

        game_over = True

        tft.draw_text_fast(
            12,
            76,
            "GAME OVER",
            RED,
            BLACK
        )

        return

    draw_piece()
    draw_next()


# ============================================================
# MOVE PIECE
# ============================================================

def move(dx, dy):

    global piece_x
    global piece_y

    new_x = piece_x + dx
    new_y = piece_y + dy

    if collision(new_x, new_y, piece_rotation):
        return False

    erase_piece()

    piece_x = new_x
    piece_y = new_y

    draw_piece()

    return True


# ============================================================
# ROTATE
# ============================================================

def rotate():

    global piece_rotation
    global piece_x

    new_rotation = (
        piece_rotation + 1
    ) % len(SHAPES[piece_type])

    # Normal rotation
    if not collision(
        piece_x,
        piece_y,
        new_rotation
    ):

        erase_piece()

        piece_rotation = new_rotation

        draw_piece()

        return

    # Try one block left
    if not collision(
        piece_x - 1,
        piece_y,
        new_rotation
    ):

        erase_piece()

        piece_x -= 1
        piece_rotation = new_rotation

        draw_piece()


# ============================================================
# LOCK PIECE
# ============================================================

def lock_piece():

    for cx, cy in get_shape():

        col = piece_x + cx
        row = piece_y + cy

        if 0 <= row < ROWS:

            board[row][col] = COLORS[piece_type]

    clear_lines()
    spawn_piece()


# ============================================================
# HARD DROP
# ============================================================

def hard_drop():

    while move(0, 1):
        pass

    lock_piece()


# ============================================================
# LINE CLEAR
# ============================================================

def clear_lines():

    global score
    global level
    global lines
    global board

    new_board = []

    cleared = 0

    for row in board:

        if all(cell is not None for cell in row):

            cleared += 1

        else:

            new_board.append(row)

    if cleared == 0:
        return

    # Add empty rows at top
    while len(new_board) < ROWS:

        new_board.insert(
            0,
            [None] * COLS
        )

    # Simple scoring
    score += cleared * 100 * level

    lines += cleared

    level = 1 + lines // 10

    board = new_board

    draw_board()

    draw_ui()


# ============================================================
# START SCREEN
# ============================================================

def start_screen():

    tft.fill_screen(BLACK)

    tft.draw_text_fast(
        48,
        20,
        "TETRIS",
        WHITE,
        BLACK
    )

    tft.draw_text_fast(
        10,
        50,
        "JOYSTICK = MOVE",
        CYAN,
        BLACK
    )

    tft.draw_text_fast(
        10,
        68,
        "A = ROTATE",
        WHITE,
        BLACK
    )

    tft.draw_text_fast(
        10,
        86,
        "B = DROP",
        WHITE,
        BLACK
    )

    tft.draw_text_fast(
        10,
        104,
        "A = START",
        WHITE,
        BLACK
    )

    while True:

        if btn_rotate.value():
            return

        time.sleep_ms(20)


# ============================================================
# MAIN GAME
# ============================================================

def main():

    global paused
    global game_over
    global score
    global level
    global lines
    global board
    global next_piece

    start_screen()

    # Reset game
    board = [
        [None for x in range(COLS)]
        for y in range(ROWS)
    ]

    score = 0
    level = 1
    lines = 0

    paused = False
    game_over = False

    next_piece = random_piece()

    draw_ui()
    spawn_piece()

    last_gravity = time.ticks_ms()
    last_move_x = time.ticks_ms()

    old_rotate = False
    old_drop = False
    old_pause = False

    while True:

        now = time.ticks_ms()

        # ----------------------------------------------------
        # PAUSE
        # ----------------------------------------------------

        pause_button = btn_pause.value()

        if pause_button and not old_pause:

            if game_over:
                main()
                return

            paused = not paused

            if paused:

                tft.draw_text_fast(
                    20,
                    76,
                    "PAUSED",
                    WHITE,
                    BLACK
                )

            else:

                # Cheap redraw: just the board + current piece,
                # not a full screen wipe/rebuild like draw_ui()
                draw_board()
                draw_piece()

        old_pause = pause_button

        if paused or game_over:

            time.sleep_ms(50)
            continue

        # ----------------------------------------------------
        # JOYSTICK LEFT / RIGHT
        # ----------------------------------------------------

        x = joystick(x_axis)

        if abs(x) > 40:

            if time.ticks_diff(now, last_move_x) >= MOVE_REPEAT:

                move(1 if x > 0 else -1, 0)

                last_move_x = now

        else:

            last_move_x = now - MOVE_REPEAT

        # ----------------------------------------------------
        # ROTATE
        # ----------------------------------------------------

        rotate_button = btn_rotate.value()

        if rotate_button and not old_rotate:
            rotate()

        old_rotate = rotate_button

        # ----------------------------------------------------
        # HARD DROP
        # ----------------------------------------------------

        drop_button = btn_drop.value()

        if drop_button and not old_drop:
            hard_drop()
            last_gravity = now

        old_drop = drop_button

        # ----------------------------------------------------
        # SOFT DROP
        # ----------------------------------------------------

        y = joystick(y_axis)

        if y < -40:
            gravity_time = SOFT_DROP
        else:
            gravity_time = max(
                120,
                GRAVITY - (level - 1) * 40
            )

        # ----------------------------------------------------
        # GRAVITY
        # ----------------------------------------------------

        if time.ticks_diff(now, last_gravity) >= gravity_time:

            if not move(0, 1):
                lock_piece()

            last_gravity = now

        time.sleep_ms(30)


# ============================================================
# RUN
# ============================================================

main()