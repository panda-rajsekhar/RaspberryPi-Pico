SOURCE = "glcdfont.c"
OUTPUT = "fonts.py"

font_bytes = []

inside = False

with open(SOURCE, "r") as f:

    for line in f:

        if "font[]" in line:
            inside = True
            continue

        if not inside:
            continue

        if "};" in line:
            break

        line = line.split("//")[0]

        parts = line.split(",")

        for part in parts:

            part = part.strip()

            if part.startswith("0x"):
                font_bytes.append(int(part, 16))

# Skip ASCII 0-31
start = 32 * 5

# Stop at ASCII 126
end = (126 + 1) * 5

font = font_bytes[start:end]

with open(OUTPUT, "w") as f:

    f.write('"""\n')
    f.write("fonts.py\n")
    f.write("Classic 5x7 ASCII Font\n")
    f.write('"""\n\n')

    f.write("FONT_5X7 = [\n")

    for i in range(0, len(font), 5):

        ascii_code = 32 + i // 5
        ch = chr(ascii_code)

        if ch == "\\":
            ch = "\\\\"

        elif ch == "'":
            ch = "\\'"

        f.write(f"    # {ascii_code} '{ch}'\n")
        f.write("    ")

        for b in font[i:i+5]:
            f.write(f"0x{b:02X}, ")

        f.write("\n\n")

    f.write("]\n")

print("fonts.py generated successfully!")
