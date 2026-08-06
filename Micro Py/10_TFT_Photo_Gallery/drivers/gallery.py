"""
JAI JAGANNATH
=========================================
Image Gallery
=========================================

Displays .pimg images.
"""

from time import sleep_ms
from image import Image

class Gallery:

    def __init__(self, display, keypad):

        self.display = display
        self.keypad = keypad
        

    # ------------------------------------
    # Open Gallery
    # ------------------------------------

    def run(self, path, images, current):

        """
        images  : list of image filenames
        current : starting image index
        """
        self.path  = path
        index = current

        while True:

            # ------------------------------
            # Display Image
            # ------------------------------

            # Clear previous image
            self.display.fill_screen(0)

            # Full path
            filename = self.path + "/" + images[index]

            # Draw image
            img = Image(filename)
            img.draw(self.display, 0, 0)

            # ------------------------------
            # Keys
            # ------------------------------

            key = self.keypad.get_key()

            if key:
                    print(key)


            if key is None:
                continue

            # Next
            if key == "S7":

                index = (index + 1) % len(images)

            # Previous
            elif key == "S5":

                index = (index - 1) % len(images)

            # Exit
            elif key == "S8":
                key = self.keypad.get_key()

                return