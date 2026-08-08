# Pico Arcade

A collection of small, self-contained games for the **Raspberry Pi Pico**, each
built around a different input device or display so the repo doubles as a
reference for wiring up various peripherals in MicroPython.

`snake.py` (matrix keypad + SPI TFT) is the flagship example the rest of this
repo follows the same conventions as — see Adding a New Game below.

---

## Why This Repo Exists

Most Pico game tutorials stop at "blink an LED" or use a single input method.
This repo instead collects several small, complete games, each deliberately
built around a **different input medium** (matrix keypad, tactile buttons,
rotary encoder, analog joystick, IR remote) so you can:

- See how the same core game-loop pattern (non-blocking input polling,
  decoupled from a fixed-rate game tick) adapts to different hardware.
- Copy-paste a working driver for whichever input device you have on hand.
- Compare trade-offs — e.g. a 4×4 matrix keypad gives you named buttons and
  cheap wiring, while an analog joystick gives you continuous direction but
  needs an ADC.

---

## Hardware Used Across the Directory
(Including Future Projects )

| Component | Used For | Notes |
|---|---|---|
| **Raspberry Pi Pico / Pico W** | All games | RP2040, MicroPython firmware |
| **ST7735 SPI TFT (128×160)** | Snake, most grid-based games | `st7735_dev.py` driver, RGB565 colors via `colors.py` |
| **SSD1306 / SH1106 OLED (128×64, I2C)** | Lightweight/monochrome games | Lower pin count than SPI TFT, good for battery builds |
| **4×4 matrix keypad** | Snake | `keypad.py` — row/col scan, no extra ICs needed |
| **Tactile push buttons (4–6x)** | Simple reflex/runner games | One GPIO per button, internal pull-ups |
| **Analog joystick module (2-axis + click)** | Games needing continuous direction | Requires ADC-capable pins (`machine.ADC`) |
| **Rotary encoder + push switch** | Menu-driven / puzzle games | Good for "select and confirm" style input, avoids debounce headaches of buttons |
| **Passive/active buzzer** | Sound effects across several games | PWM on a single GPIO |
| **IR receiver (TSOP-style) + remote** | Couch-friendly games | Lets you reuse a cheap remote instead of a custom keypad |
| **MicroSD breakout (SPI)** | High-score persistence | Optional, used where a game saves state between boots |

Each game's header docstring lists exactly which of these it needs — you
don't need all of them to run any single game.

---

## Current Repo Layout

```
Games
│   README.md
└───/01_Snake_MicroPython
└───/02_Dino_Run_MicroPython

```

Every game is self-contained in its own folder and only imports the drivers
it actually needs from `drivers/`.

---

## Games

| Game | Display | Input | Highlights |
|---|---|---|---|
| **Snake** | ST7735 TFT | 4×4 matrix keypad | Non-blocking input scan, gradual snake growth, timed bonus "master treat" item |
| **Pong** | ST7735 TFT | 2 tactile buttons per player | Two-player local, simple ball-physics reflection |
| **Memory Match** | SSD1306 OLED | Rotary encoder + click | Encoder-driven cursor, tile flip/match logic |
| **Flappy-style** | ST7735 TFT | 1 tactile button | Gravity + single-input "flap" mechanic |
| **Breakout** | ST7735 TFT | Analog joystick | Continuous paddle movement via ADC read |

> Each game folder has its own short README covering exact wiring, controls,
> and any game-specific constants worth tuning.
> The above mentioned projects are key highlight and I have many more planned. 

---

## Shared Drivers

All display/input drivers live in `drivers/` and are written to be dropped
into any game with a one-line import — none of them assume a specific game
is using them.

- **`st7735_dev.py`** — thin wrapper exposing `fill_screen`, `fill_rectangle`,
  `draw_rectangle`, and `draw_text_fast` over the ST7735 SPI driver.
- **`colors.py`** — RGB565 constants (`RED`, `GREEN`, `BLUE`, `CYAN`,
  `YELLOW`, `MAGENTA`, `WHITE`, `BLACK`, …) shared by every TFT-based game.
- **`keypad.py`** — wraps a 4×4 matrix keypad's row/column GPIO pins and a
  `keys[row][col]` lookup table (see `snake.py`'s docstring for the default
  layout).
- **`buttons.py`** — a small debounce helper around `machine.Pin` for
  straightforward push-button input.
- **`joystick.py`** — reads two `machine.ADC` channels and a click pin,
  returning a normalized `(x, y, pressed)` tuple.
- **`encoder.py`** — quadrature decoding for a rotary encoder plus its
  integrated push switch.
- **`ir_remote.py`** — decodes standard NEC-protocol IR remote codes into
  named button events.
---

## Wiring Notes

Exact pin assignments are intentionally left to each game's driver
instantiation (`ST7735()`, `Keypad()`, etc.) rather than hardcoded in this
README, since they're easy to remap. As a starting point:

| Interface | Typical Pico pins |
|---|---|
| SPI (ST7735 TFT) | SCK, MOSI, CS, DC, RST — any SPI0/SPI1-capable GPIOs |
| I2C (SSD1306 OLED) | SDA, SCL — any I2C0/I2C1-capable GPIOs |
| 4×4 matrix keypad | 8 GPIOs total (4 rows + 4 cols) |
| Tactile buttons | 1 GPIO per button, `Pin.PULL_UP`, wired to GND |
| Analog joystick | 2 ADC-capable GPIOs (26–28) + 1 digital click pin |
| Rotary encoder | 2 GPIOs for quadrature (A/B) + 1 for the push switch |
| IR receiver | 1 GPIO (digital in), decoded via `machine.Pin` IRQ |

Full per-game pinout tables live under `docs/wiring/`.

---

## Adding a New Game

To keep the directory consistent, new games should follow the pattern
established by `snake.py`:

1. **Non-blocking input, decoupled from the game tick.** Poll input on a
   short loop (a few ms), but only advance game state on a fixed interval
   (`TICK_MS`-style constant) so speed is tunable independent of input
   responsiveness.
2. **Constants up top.** Grid size, colors, timing, and scoring values
   should be named constants near the top of the file, not magic numbers
   buried in logic — makes tuning and re-wiring painless.
3. **One state block.** Keep game state (score, position, entities) in a
   small set of clearly-commented globals, mutated only through explicit
   `global` declarations inside functions — no hidden state.
4. **A `reset_game()` you can call more than once.** Games should be
   restartable without rebooting the Pico.
5. **Reuse drivers, don't fork them.** If an existing driver in `drivers/`
   almost fits, extend it there rather than copy-pasting a modified version
   into your game folder.
6. **A short per-game README** covering: required hardware, wiring, controls,
   and any constants worth tweaking.

---

## Design Conventions

- **Grid-based over pixel-based** movement where possible — simpler
  collision logic and forgiving of a TFT's modest resolution.
- **Score and state feedback drawn incrementally** (redraw only the score
  bar or the cells that changed) rather than redrawing the whole screen
  every frame, to keep frame times low on the RP2040's SPI/I2C bandwidth.
- **Timed/limited-availability bonus mechanics** (like Snake's master treat)
  are encouraged — they exercise real-time (`ticks_ms`/`ticks_diff`) logic
  independent of the game tick, which is good practice for anything
  animation- or event-driven on this hardware.

---

## Roadmap / Ideas

- [ ] Tetris-style game using the rotary encoder for rotate + soft drop
- [ ] Simple racing game using the IR remote
- [ ] High-score persistence via the microSD breakout
- [ ] Shared `game_engine.py` helper module to further cut boilerplate
      across games (tick loop, edge-triggered input helper, etc.)

Contributions welcome — open a PR with your game following the conventions
above, or open an issue if you'd like to suggest a new input device to
target.

---

## License

MIT — see `LICENSE`. Feel free to fork, remix, and build your own cabinet
full of tiny Pico games.

### Authors Note 
# Author's Note

## Author's Note

This repository exists for one reason: **to learn.**

I am not a game developer, and I don't claim to be one. These projects are simply my way of learning embedded systems by writing software that runs on real hardware.

Games are a fun excuse to explore concepts like graphics rendering, input handling, timing, state machines, collision detection, memory management, and hardware interfacing on the Raspberry Pi Pico.

Most of these games are inspired by the simple classics I remember from retro feature phones—games I enjoyed, or sometimes wished I had played more. Recreating them has been both a nostalgic experience and a practical programming exercise.

The code in this repository reflects my current understanding. As I continue learning, I expect to revisit these projects, improve the implementations, and occasionally rewrite them from scratch. That evolution is part of the purpose of keeping this repository public.

If you're also learning MicroPython, embedded systems, or graphics programming on small microcontrollers, I hope these examples help you build your own projects.

**This repository is not about becoming a game developer. It's about becoming a better embedded systems programmer by building software on real hardware.**

Happy coding! 🚀
