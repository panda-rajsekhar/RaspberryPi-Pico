"""
JAI JAGANNATH
=========================================
SD File Browser
=========================================
"""

from st7735_dev import ST7735
from colors import *
from mount_sd import mount_sd
from keypad import Keypad
from gallery import Gallery
from time import ticks_ms, ticks_diff
import os

# ----------------------------------------
# Initialize
# ----------------------------------------

start = ticks_ms()

display = ST7735()
keypad = Keypad()
gallery = Gallery(display, keypad)
selected = 0
current_path = "/sd"
print("Init   :", ticks_diff(ticks_ms(), start), "ms")

# ----------------------------------------
# Clear Screen
# ----------------------------------------

t0 = ticks_ms()

display.fill_screen(BLACK)

print("Screen :", ticks_diff(ticks_ms(), t0), "ms")

# ----------------------------------------
# Mount SD
# ----------------------------------------
mount_sd()
current_path = "/sd"

# -------------------------
# Define function
# -------------------------

def read_directory(path):

    directories = []
    files = []

    for name in os.listdir(path):

        if name == "System Volume Information":
            continue

        full_path = path + "/" + name

        mode = os.stat(full_path)[0]

        if mode & 0x4000:
            directories.append(name)
        else:
            files.append(name)

    directories.sort()
    files.sort()

    return directories, files, directories + files



# ----------------------------------------
# Sort Entries
# ----------------------------------------

directories, files, entries = read_directory(current_path)

# ----------------------------------------
# Draw Title
# ----------------------------------------

t0 = ticks_ms()

display.draw_text_fast(
    4,
    4,
    "SD FILE BROWSER",
    CYAN,
    BLACK
)

print("Title  :", ticks_diff(ticks_ms(), t0), "ms")

# ----------------------------------------
# Draw One Entry
# ----------------------------------------

def draw_entry(index):

    if index >= len(entries):
        return

    name = entries[index]

    if name in directories:
        text = "- " + name
    else:
        text = "  " + name

    y = 18 + index * 8

    if index == selected:
        fg = WHITE
        bg = BLUE
    else:
        fg = WHITE
        bg = BLACK

    display.draw_text_fast(
        4,
        y,
        text,
        fg,
        bg
    )
    
# ----------------------------------------
# Redraw Browser
# ----------------------------------------

def redraw_browser():

    display.fill_screen(BLACK)

    display.draw_text_fast(
        4,
        4,
        current_path,
        CYAN,
        BLACK
    )

    if len(entries) == 0:

        display.draw_text_fast(
            4,
            20,
            "< Empty >",
            DARKGRAY,
            BLACK
        )

    else:

        for i in range(len(entries)):
            draw_entry(i)

    display.draw_text_fast(
        4,
        150,
        "Items: {}".format(len(entries)),
        GREEN,
        BLACK
    )


# ----------------------------------------
# Read Directory
# ----------------------------------------

def read_directory(path):

    directories = []
    files = []

    for name in os.listdir(path):

        if name == "System Volume Information":
            continue

        full_path = path + "/" + name

        mode = os.stat(full_path)[0]

        if mode & 0x4000:
            directories.append(name)
        else:
            files.append(name)

    directories.sort()
    files.sort()

    return directories, files, directories + files

# ----------------------------------------
# Draw File List
# ----------------------------------------

t0 = ticks_ms()

for i in range(len(entries)):

    draw_entry(i)

print("Files  :", ticks_diff(ticks_ms(), t0), "ms")

# ----------------------------------------
# Footer
# ----------------------------------------

t0 = ticks_ms()

display.draw_text_fast(
    4,
    150,
    "Items: {}".format(len(entries)),
    GREEN,
    BLACK
)

print("Footer :", ticks_diff(ticks_ms(), t0), "ms")

print("Total  :", ticks_diff(ticks_ms(), start), "ms")

# ----------------------------------------
# Navigation Loop
# ----------------------------------------

while True:

    key = keypad.get_key()

    if key is None:
        continue

    old = selected

    # Move Up
    if key == "S2":

        if selected > 0:
            selected -= 1

    # Move Down
    elif key == "S10":

        if selected < len(entries) - 1:
            selected += 1

    # Redraw only changed rows
    if old != selected:

        draw_entry(old)
        draw_entry(selected)
    # Open Folder
        # Open Folder
    elif key == "S7":

        if len(entries) == 0:
            continue

        if entries[selected] in directories:

            current_path += "/" + entries[selected]

            directories, files, entries = read_directory(current_path)

            selected = 0

            redraw_browser()

            continue
    # Back
        
    elif key == "S5":

        if current_path != "/sd":

            current_path = current_path.rsplit("/", 1)[0]

            directories, files, entries = read_directory(current_path)

            selected = 0

            redraw_browser()

            continue
        
    #Open Pimg
    elif key == "S4":

        if len(entries) == 0:
            continue

        name = entries[selected]

        if name.endswith(".pimg"):

            images = []
            image_index = 0

            for entry in entries:

                if entry.endswith(".pimg"):

                    if entry == name:
                        image_index = len(images)

                    images.append(entry)
                    
            gallery.run(current_path, images, image_index)            

            redraw_browser()
