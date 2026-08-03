#jai jagannath

from PIL import Image
import struct

# ============================================================
# Configuration
# ============================================================

INPUT_FILE = "../assets/logo.png"
OUTPUT_FILE = "../assets/logo.pimg"

OUTPUT_WIDTH = 128
OUTPUT_HEIGHT = 160

MAGIC = b"PIMG"
PIXEL_FORMAT = 0x01  # RGB565


# ============================================================
# Image Loading
# ============================================================

def load_image(path):
    image = Image.open(path)

    print(f"Image Mode : {image.mode}")

    if image.mode != "RGB":
        print(f"Converting {image.mode} -> RGB")
        image = image.convert("RGB")
    else:
        print("Image already in RGB format.")

    return image


# ============================================================
# Image Information
# ============================================================

def image_info(image):

    print("\nImage Information")
    print("-" * 30)

    print(f"Width  : {image.width}")
    print(f"Height : {image.height}")
    print(f"Mode   : {image.mode}")
    print(f"Pixels : {image.width * image.height}")


# ============================================================
# Resize
# ============================================================

def resize_image(image, width, height):

    print("\nResizing Image")
    print("-" * 30)

    print(f"Old Resolution : {image.width} x {image.height}")
    print(f"New Resolution : {width} x {height}")

    return image.resize(
        (width, height),
        Image.Resampling.LANCZOS
    )


# ============================================================
# RGB888 -> RGB565
# ============================================================

def rgb888_to_rgb565(r, g, b):

    return (
        ((r & 0xF8) << 8) |
        ((g & 0xFC) << 3) |
        (b >> 3)
    )


# ============================================================
# Write PIMG
# ============================================================

def write_pimg(image, filename):

    print("\nWriting PIMG File")
    print("-" * 30)

    with open(filename, "wb") as file:

        # Magic Number
        file.write(MAGIC)

        # Width
        file.write(struct.pack("<H", image.width))

        # Height
        file.write(struct.pack("<H", image.height))

        # Pixel Format
        file.write(struct.pack("<B", PIXEL_FORMAT))

        # Reserved
        file.write(b"\x00\x00\x00")

        # Pixels
        for y in range(image.height):

            for x in range(image.width):

                r, g, b = image.getpixel((x, y))

                rgb565 = rgb888_to_rgb565(r, g, b)

                file.write(struct.pack(">H", rgb565))

    print("Done.")
    print(f"Saved : {filename}")


# ============================================================
# Main
# ============================================================

def main():

    image = load_image(INPUT_FILE)

    image_info(image)

    image = resize_image(
        image,
        OUTPUT_WIDTH,
        OUTPUT_HEIGHT
    )

    image_info(image)

    write_pimg(image, OUTPUT_FILE)


if __name__ == "__main__":
    main()
