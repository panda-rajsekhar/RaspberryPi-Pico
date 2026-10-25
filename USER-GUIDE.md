# Why ??

This repository is documented as of my learning experience with Pico and all the hardware in my personal inventory . New experiments are pushed 
when the components are available with me physically since every experiment is performed on Real hardware with breadboard and DuPont connectors.

So far i have attempted to document ever experiment while keeping in mind the fact to give the reader an insight of what is happening in that loop 
when the code is running inside the controller. And since this is the Classic Pico without Wifi or Bluetooth we are left out significantly with the
IOT perspective of the Embedded Systems. To follow on the IOT side I have planned to get myself a Pico 2W asap. However lets stick to the point that 
why a user guide ? 

Since the repository is growing there is a need of my viewpoint on how the user is using this repository. 

### Getting Started 

- First of all , get your basics done with the help of other embedded Dev boards like Arduino or ESP.
- Clear your foundations there and most importantly develop the logic of `how to get things done` !
- Then if you are good in C / C++ you will easily adapt to micro python logic.

## How to Use / Study The Repository 
- The basics of getting started is in the Root Directory's `README`.
- From there you will get the idea on how to get started wit Pico in Micro Python.
- Next you must head on to the   `Micro Python` directory where you will get a structured list of the experiments.
- After you have completed performing and understanding the Micro Python Side head on to the Games.
- Then you are efficient enough to do the Projects in your own manner.

## My Goal with this Repo 
I will keep including newer experiments as i get my hands on to the hardware. Then for the Drivers part I will attempt to optimize them in C (No HAL if possible) 
to get the maximum resource utilization. and final goal is to have a cyber-deck with Pico. 


## Current Repo Structure 

``` shell
PS D:\RaspberryPi-Pico-main\RaspberryPi-Pico-main> tree /f
Folder PATH listing for volume New Volume
Volume serial number is 6846-8396
D:.
│   LICENSE
│   Readme.md
│   USER-GUIDE.md
│
├───Assets
│       blink.jpg
│       ckp1.png
│       cktpy-firmwhere.png
│       cktpy-frmwhere.png
│       cktpy-ssfl.png
│       download.png
│       File1.png
│       File2.png
│       IMG_20260726_131444.jpg
│       pico-drive.png
│       rp1-rp2.png
│       thonny 1.png
│       Thonny.png
│       Transfer.png
│       verification.png
│
├───Games
│   │   README.md
│   │
│   ├───01_Snake_MicroPython
│   │   │   README.md
│   │   │   snake.py
│   │   │
│   │   ├───Assets
│   │   │       00_Setup.jpg
│   │   │       01_Display_Controls.jpg
│   │   │       02_Start_screen.jpg
│   │   │       03_Master_Eat.jpg
│   │   │       04_Pause.jpg
│   │   │       05_Game_Over.jpg
│   │   │
│   │   └───Driver
│   │           colors.py
│   │           keypad.py
│   │           st7735_dev.py
│   │           widgets_dev.py
│   │
│   ├───02_Dino_Run_MicroPython
│   │   │   Dino.py
│   │   │   README.md
│   │   │
│   │   └───assets
│   │           00_Circuit_Setup.jpg
│   │           01_Controls.jpg
│   │           02_Home_Screen.jpg
│   │           03_Running.jpg
│   │           04_Game_Over.jpg
│   │
│   ├───03_Tetris_MicroPython
│   │   │   main.py
│   │   │   README.md
│   │   │
│   │   └───assets
│   │           00_Circuit_Setup.jpg
│   │           02_high_score.jpg
│   │           02_home_screen.jpg
│   │
│   └───04_Dice
│       │   dice_roll.py
│       │   README.md
│       │
│       └───assets
│               00_Circuit.jpg
│               1.jpg
│               2.jpg
│               3.jpg
│               4.jpg
│               5.jpg
│               6.jpg
│
├───Micro Py
│   ├───01_Onboard LED
│   │       blink.md
│   │       blink.py
│   │
│   ├───02_External_LED
│   │   │   alternae_pair.py
│   │   │   filling_bar.py
│   │   │   ping_pong.py
│   │   │   README.md
│   │   │   running.py
│   │   │
│   │   └───images
│   │           alt_pair.gif
│   │           ckt.jpg
│   │           ext_led1.gif
│   │           filling.gif
│   │           pong.gif
│   │           running.gif
│   │
│   ├───03_8Bit_LED_Manipulation
│   │   │   01_test.py
│   │   │   02_Binary_Counter.py
│   │   │   03_Shifters.py
│   │   │   04_Bitwise_And.py
│   │   │   05_Bitwise_OR.py
│   │   │   06_Bitwise_XOR.py
│   │   │   README.md
│   │   │
│   │   └───Assets
│   │           and.gif
│   │           circuit.heic
│   │           circuit.jpg
│   │           counter.gif
│   │           or.gif
│   │           shifter.gif
│   │           test.gif
│   │           xor.gif
│   │
│   ├───04_Buttons_Switches
│   │   │   README.md
│   │   │
│   │   ├───Assets
│   │   │       button.gif
│   │   │       button_module.jpg
│   │   │       keypad.gif
│   │   │       keypad.jpg
│   │   │       keypad_setup.jpg
│   │   │
│   │   ├───Button
│   │   │       01_Button_Control_Onboard_LED.py
│   │   │
│   │   └───Keypad
│   │           01_4x4_Matrix_Keypad.py
│   │           02_Keypad_LED_Blink.py
│   │
│   ├───05_16x2_LCD_i2c
│   │   │   01_I2C_Scan.py
│   │   │   02_hello.py
│   │   │   03_cursor_positioning.py
│   │   │   04_clear_home.py
│   │   │   05_scroll.py
│   │   │   06_display_demo.py
│   │   │   07_custom_characters.py
│   │   │   README.md
│   │   │   Read_i2c.md
│   │   │
│   │   ├───assets
│   │   │       clear_home.gif
│   │   │       cursor_positioning.jpg
│   │   │       custom_characters.jpg
│   │   │       display_demo.gif
│   │   │       helllo_world.jpg
│   │   │       i2c_adapter.jpg
│   │   │       scroll.gif
│   │   │       setup.jpg
│   │   │
│   │   └───lcd
│   │           i2c_lcd.py
│   │           lcd_api.py
│   │
│   ├───06_1.8inch_TFT_LCD
│   │   │   01_SPI_Test.py
│   │   │   02_Display_Initialization.py
│   │   │   03_Color_Showcase.py
│   │   │   04_Draw_Pixel.py
│   │   │   05_Corner_Test.py
│   │   │   06_Crosshair_Test.py
│   │   │   07_Lines_Test.py
│   │   │   08_Starburst.py
│   │   │   09_Rectangles_Test.py
│   │   │   10_Nested_Rectangles.py
│   │   │   11_Multiple_Filled_Rectangles.py
│   │   │   12_Circle_Test.py
│   │   │   13_Olympic_Rings.py
│   │   │   14_Multiple_Filled_Circles.py
│   │   │   15_Traffic_Signal.py
│   │   │   16_Triangles_Test.py
│   │   │   17_Sierpinski_Style_Pattern.py
│   │   │   18_Filled_Triangles_Tessellation.py
│   │   │   19_Christmas_Tree.py
│   │   │   20_Font_Test.py
│   │   │   21_Draw_Character.py
│   │   │   22_Text_Showcase.py
│   │   │   23_Text_Color_Showcase.py
│   │   │   24_Text_Scaling.py
│   │   │   25_Progress_Bar.py
│   │   │   26_Text_Background_Test.py
│   │   │   27_Draw_Panel.py
│   │   │   28_Draw_Status_LED.py
│   │   │   29_Draw_Graph.py
│   │   │   30_Diamonds_Test.py
│   │   │   31_Meter_Test.py
│   │   │   32_Button_Test.py
│   │   │   33_Battery_Test.py
│   │   │   README.md
│   │   │
│   │   ├───assets
│   │   │       00_circuit.jpg
│   │   │       01_01_SPI_Test.jpg
│   │   │       04_Draw_Pixel.jpg
│   │   │       05_Corner_Test.jpg
│   │   │       06_Crosshair_Test.jpg
│   │   │       07_Lines_Test.jpg
│   │   │       09_Rectangles_Test.jpg
│   │   │       11_Multiple_Filled_Rectangles.jpg
│   │   │       12_Circle_Test.jpg
│   │   │       13_Olympic_Rings.jpg
│   │   │       14_Multiple_Filled_Circles.jpg
│   │   │       15_Traffic_Signal.jpg
│   │   │       16_Triangles_Test.jpg
│   │   │       17_Sierpinski_Style_Pattern.jpg
│   │   │       18_Filled_Triangles_Tessellation.jpg
│   │   │       19_Christmas_Tree.jpg
│   │   │       24_Text_Scaling.jpg
│   │   │       27_Draw_Panel.jpg
│   │   │       28_Draw_Status_LED.jpg
│   │   │       29_Draw_Graph.jpg
│   │   │       30_Diamonds_Test.jpg
│   │   │       31_Meter_Test.jpg
│   │   │       32_Button_Test.jpg
│   │   │       33_Battery_Test.jpg
│   │   │       under construction.png
│   │   │
│   │   └───lcd
│   │           colors.py
│   │           fonts.py
│   │           st7735.py
│   │           widgets.py
│   │
│   ├───07_Pico_Resource_Monitor_UI
│   │   │   main.py
│   │   │   monitor.py
│   │   │   README.md
│   │   │
│   │   └───assets
│   │           00_circuit.jpg
│   │           01_Static_UI.jpg
│   │
│   ├───08_TFT_PICO_Image_Processing
│   │   │   image.py
│   │   │   README.md
│   │   │   test.py
│   │   │
│   │   ├───assets
│   │   │       01_v1_output.jpg
│   │   │       file_upload.png
│   │   │       logo.pimg
│   │   │       logo.png
│   │   │
│   │   └───tools
│   │           image_converter.py
│   │
│   ├───09_SD_Card_Storage_Expansion
│   │   │   display.py
│   │   │   mount_sd.py
│   │   │   move.py
│   │   │   README.md
│   │   │   sd_verification.py
│   │   │   unmount_sd.py
│   │   │
│   │   ├───assets
│   │   │       00_sd_cardslot.jpg
│   │   │       01_circuit_wiring.jpg
│   │   │       02_output.jpg
│   │   │
│   │   └───driver
│   │           sdcard.py
│   │
│   ├───10_TFT_Photo_Gallery
│   │   │   main.py
│   │   │   README.md
│   │   │
│   │   ├───drivers
│   │   │       colors.py
│   │   │       fonts.py
│   │   │       gallery.py
│   │   │       image.py
│   │   │       keypad.py
│   │   │       mount_sd.py
│   │   │       sdcard.py
│   │   │       sd_verification.py
│   │   │       st7735_dev.py
│   │   │       widgets_dev.py
│   │   │
│   │   └───gallery
│   │           00_circuit.jpg
│   │           01_file_browser_ui.jpg
│   │           02_inside_folder_1.jpg
│   │           02_inside_folder_2.jpg
│   │           03_working_output_1.mp4
│   │           03_working_output_2.mp4
│   │
│   ├───11_Joystick_Controller
│   │   │   main.py
│   │   │   README.md
│   │   │
│   │   └───assets
│   │           00_Ckt.jpg
│   │           01_homescreen.jpg
│   │           03_Double_Button_Press.jpg
│   │           03_four_press.jpg
│   │           03_Single_Button_Press.jpg
│   │           03_Triple_Button_Press.jpg
│   │           04_joystick_movement_1.jpg
│   │           04_joystick_movement_2.jpg
│   │           04_joystick_movement_3.jpg
│   │           04_joystick_movement_4.jpg
│   │
│   ├───12_8x8_Matrix_Led
│   │   │   01_Test.py
│   │   │   02_Box.py
│   │   │   02_Checkboard.py
│   │   │   02_X.py
│   │   │   03_Mix_Pattern.py
│   │   │   04_Text.py
│   │   │   README.md
│   │   │
│   │   └───assets
│   │           00_circuit.jpg
│   │           01_test.jpg
│   │           02_box.jpg
│   │           02_checkboard.jpg
│   │           02_x.jpg
│   │
│   ├───13_FC-51_Object_Detection
│   │   │   README.md
│   │   │   test.py
│   │   │
│   │   └───assets
│   │           00_Circuit.jpg
│   │           01_nd.jpg
│   │           02_d.jpg
│   │
│   ├───14_HC-SR04_Distance_Measurement
│   │   │   main.py
│   │   │   README.md
│   │   │
│   │   └───assets
│   │           00_Ckt.jpg
│   │           01_det.jpg
│   │
│   ├───15_RFID-RC522
│   │   │   README.md
│   │   │   rfid.py
│   │   │
│   │   └───assets
│   │           00_ckt.jpg
│   │           01_rfid.jpg
│   │
│   ├───16_Servo-PWM
│   │   │   angle.py
│   │   │   README.md
│   │   │   servo_test.py
│   │   │   test.py
│   │   │
│   │   └───assets
│   │           00_ckt.jpg
│   │           01_working.gif
│   │           s1.jpg
│   │           s2.jpg
│   │           s3.jpg
│   │           s4.jpg
│   │
│   ├───17_Neo_Pixel_Ring_With_TFT
│   │   │   main.py
│   │   │   README.md
│   │   │
│   │   └───assets
│   │           00_led.jpg
│   │           01_setup.jpg
│   │           02_output.gif
│   │
│   └───18_GPS
│       │   main.py
│       │   README.md
│       │
│       ├───advanced
│       │       adv-gps.py
│       │       Output.md
│       │
│       └───assets
│               02.jpg
│               03.jpg
│
└───Projects
    ├───Drivers
    │       colors.py
    │       ds1302.py
    │       fonts.py
    │       i2c_lcd.py
    │       lcd_api.py
    │       st7735.py
    │       widgets.py
    │
    ├───Pico-Morse
    │   │   main.py
    │   │   README.md
    │   │
    │   └───assets
    │           00-kct.jpg
    │           01_idle.jpg
    │
    ├───Pico-Oscilloscope
    │   │   oscilloscope.py
    │   │   README.md
    │   │
    │   └───assets
    │           00_Connections.jpg
    │
    └───Pico-RTC-Clock
        │   main.py
        │   README.md
        │
        └───assets
                00ckt.jpg
                01clk.jpg
``` 
