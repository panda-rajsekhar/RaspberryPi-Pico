from image import Image
from st7735 import ST7735

display = ST7735()

logo = Image("logo.pimg")

logo.draw(display, 0, 0)