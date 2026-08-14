from machine import Pin, SPI
from time import sleep

spi = SPI(
    0,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19)
)
cs = Pin(17, Pin.OUT)
cs.value(1)

def write_reg(reg, data):
    cs.value(0)
    spi.write(bytes([reg, data]))
    cs.value(1)

def show(row_bytes):
    for row in range(8):
        write_reg(row + 1, row_bytes[row])

# --- MAX7219 setup ---
write_reg(0x0C, 0x01)  # shutdown -> normal operation
write_reg(0x09, 0x00)  # decode mode -> no decode (raw bitmap)
write_reg(0x0B, 0x07)  # scan limit -> all 8 digits/rows
write_reg(0x0A, 0x08)  # intensity (0x00 dim - 0x0F bright)
write_reg(0x0F, 0x00)  # display test -> off

# =========================================================
# FONT — each glyph is 5 rows x 3 columns, '#' = lit pixel.
# Written as row-strings so there's no manual byte math.
# =========================================================
FONT = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'],
    'B': ['##.', '#.#', '##.', '#.#', '##.'],
    'C': ['.##', '#..', '#..', '#..', '.##'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '##.', '#..', '###'],
    'F': ['###', '#..', '##.', '#..', '#..'],
    'G': ['.##', '#..', '#.#', '#.#', '.##'],
    'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'],
    'J': ['..#', '..#', '..#', '#.#', '.#.'],
    'K': ['#.#', '#.#', '##.', '#.#', '#.#'],
    'L': ['#..', '#..', '#..', '#..', '###'],
    'M': ['#.#', '###', '###', '#.#', '#.#'],
    'N': ['#.#', '###', '###', '###', '#.#'],
    'O': ['.#.', '#.#', '#.#', '#.#', '.#.'],
    'P': ['##.', '#.#', '##.', '#..', '#..'],
    'Q': ['.#.', '#.#', '#.#', '.#.', '..#'],
    'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['.##', '#..', '.#.', '..#', '##.'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '.#.'],
    'V': ['#.#', '#.#', '#.#', '.#.', '.#.'],
    'W': ['#.#', '#.#', '###', '###', '#.#'],
    'X': ['#.#', '#.#', '.#.', '#.#', '#.#'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'],
    'Z': ['###', '..#', '.#.', '#..', '###'],
    '0': ['###', '#.#', '#.#', '#.#', '###'],
    '1': ['.#.', '##.', '.#.', '.#.', '###'],
    '2': ['###', '..#', '###', '#..', '###'],
    '3': ['###', '..#', '###', '..#', '###'],
    '4': ['#.#', '#.#', '###', '..#', '..#'],
    '5': ['###', '#..', '###', '..#', '###'],
    '6': ['###', '#..', '###', '#.#', '###'],
    '7': ['###', '..#', '..#', '..#', '..#'],
    '8': ['###', '#.#', '###', '#.#', '###'],
    '9': ['###', '#.#', '###', '..#', '###'],
    ' ': ['...', '...', '...', '...', '...'],
    '.': ['...', '...', '...', '...', '.#.'],
    '!': ['.#.', '.#.', '.#.', '...', '.#.'],
    '?': ['###', '..#', '.#.', '...', '.#.'],
    '-': ['...', '...', '###', '...', '...'],
    ':': ['...', '.#.', '...', '.#.', '...'],
}

def glyph_to_columns(rows):
    """5x3 glyph rows -> list of 3 column bytes (bit i = row i, i=0 top)."""
    cols = []
    for c in range(3):
        col_byte = 0
        for r in range(5):
            if rows[r][c] == '#':
                col_byte |= (1 << r)
        cols.append(col_byte)
    return cols

FONT_COLS = {ch: glyph_to_columns(rows) for ch, rows in FONT.items()}
ROW_OFFSET = 1  # shifts the 5-row font down 1 bit to vertically center in 8 rows

def text_to_column_stream(text, char_spacing=1):
    """Convert a string into one long list of column bytes (row bits, offset applied)."""
    stream = []
    for ch in text.upper():
        cols = FONT_COLS.get(ch, FONT_COLS[' '])
        for col in cols:
            stream.append(col << ROW_OFFSET)
        stream.extend([0] * char_spacing)
    return stream

def columns_to_rows(column_window):
    """8 column bytes (row bits) -> 8 row bytes (column bits), col0 = leftmost = bit7."""
    row_bytes = [0] * 8
    for col_index, col_byte in enumerate(column_window):
        for row in range(8):
            if col_byte & (1 << row):
                row_bytes[row] |= (1 << (7 - col_index))
    return row_bytes

def scroll_text(text, delay=0.05, repeat=1):
    stream = [0] * 8 + text_to_column_stream(text) + [0] * 8
    for _ in range(repeat):
        for start in range(len(stream) - 7):
            window = stream[start:start + 8]
            show(columns_to_rows(window))
            sleep(delay)

# --- Demo loop ---
while True:
    scroll_text("JAI ", delay=0.05)
    sleep(0.5)
    scroll_text("JAGANNATH", delay=0.04)
    sleep(0.5)