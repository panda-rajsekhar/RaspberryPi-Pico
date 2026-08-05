from machine import Pin, SPI
import os
import sdcard

# -------------------------------------------------
# Mount SD Card
# -------------------------------------------------
spi = SPI(
    0,
    baudrate=100000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),
    miso=Pin(16)
)

cs = Pin(5, Pin.OUT)
cs.value(1)

try:
    sd = sdcard.SDCard(spi, cs)
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
except OSError:
    pass


# -------------------------------------------------
# Main Loop
# -------------------------------------------------
while True:

    print("\n========================================")
    print("        PICO SD FILE COPY MANAGER")
    print("========================================")

    # ----------------------------
    # Show files in Pico root
    # ----------------------------
    files = []

    print("\nFiles available in Pico root:\n")

    for item in os.listdir("/"):
        try:
            os.listdir("/" + item)
        except OSError:
            files.append(item)

    if not files:
        print("No files found.")
        break

    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    print("\n0. Exit")

    # ----------------------------
    # Select source file
    # ----------------------------
    try:
        choice = int(input("\nSelect file number: "))
    except ValueError:
        print("Invalid input.")
        continue

    if choice == 0:
        print("\nGoodbye!")
        break

    if choice < 1 or choice > len(files):
        print("Invalid selection.")
        continue

    source_name = files[choice - 1]
    source_path = "/" + source_name

    # ----------------------------
    # Show SD folders
    # ----------------------------
    folders = []

    print("\nDestination folders:\n")

    for item in os.listdir("/sd"):
        try:
            os.listdir("/sd/" + item)
            folders.append(item)
        except OSError:
            pass

    if not folders:
        print("No folders found on SD card.")
        continue

    for i, folder in enumerate(folders, start=1):
        print(f"{i}. {folder}")

    print("\n0. Cancel")

    # ----------------------------
    # Select destination
    # ----------------------------
    try:
        choice = int(input("\nSelect destination folder: "))
    except ValueError:
        print("Invalid input.")
        continue

    if choice == 0:
        continue

    if choice < 1 or choice > len(folders):
        print("Invalid selection.")
        continue

    destination_folder = folders[choice - 1]
    destination_path = "/sd/{}/{}".format(destination_folder, source_name)

    # ----------------------------
    # Copy File
    # ----------------------------
    print("\nCopying...")

    try:
        with open(source_path, "rb") as src:
            with open(destination_path, "wb") as dst:
                while True:
                    data = src.read(512)
                    if not data:
                        break
                    dst.write(data)

        print("✅ Copy completed.")
        print("Source      :", source_path)
        print("Destination :", destination_path)

    except Exception as e:
        print("❌ Copy failed:", e)

    # ----------------------------
    # Continue?
    # ----------------------------
    while True:
        option = input("\nCopy another file? (Y/N): ").strip().lower()

        if option == "y":
            break

        if option == "n":
            print("\nExiting File Manager...")
            raise SystemExit

        print("Please enter Y or N.")
