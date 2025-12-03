# 🚀 Space Invaders Pro
### ESP32 Single-Button Edition

A classic Space Invaders game optimized for ESP32 with OLED display and single-button control!

![Game Status](https://img.shields.io/badge/status-playable-brightgreen)
![Platform](https://img.shields.io/badge/platform-ESP32-blue)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 📋 Table of Contents
- [Features](#-features)
- [Hardware Requirements](#-hardware-requirements)
- [Installation](#-installation)
- [How to Play](#-how-to-play)
- [Game Mechanics](#-game-mechanics)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Credits](#-credits)

---

## ✨ Features

### 🎮 Gameplay
- **50 Invaders** - 5 rows × 10 columns formation
- **Auto-movement** - Player ship moves automatically left-right
- **Single-button shooting** - Simple and intuitive control
- **Progressive difficulty** - Invaders speed up as you eliminate them
- **Score tracking** - Real-time score display with high score memory

### 🔊 Audio
- Shoot sound effect
- Hit confirmation sound
- Victory fanfare
- Game over sound

### 📊 Game States
- Active gameplay
- Victory screen (eliminate all invaders)
- Game over screen (invaders reach bottom)
- Score summary

---

## 🛠️ Hardware Requirements

### Required Components
| Component | Specification | Pin |
|-----------|---------------|-----|
| **Microcontroller** | ESP32 DevKit | - |
| **Display** | SSD1306 OLED 128×64 I2C | SCL: GPIO 22, SDA: GPIO 21 |
| **Button** | Push button with pull-up | GPIO 4 |
| **Buzzer** | Passive buzzer (PWM) | GPIO 25 |

### Wiring Diagram
```
ESP32          OLED Display
GPIO 22   →    SCL
GPIO 21   →    SDA
3.3V      →    VCC
GND       →    GND

ESP32          Button
GPIO 4    →    One side
GND       →    Other side (internal pull-up enabled)

ESP32          Buzzer
GPIO 25   →    Positive (+)
GND       →    Negative (-)
```

---

## 📥 Installation

### Prerequisites
1. **MicroPython** installed on ESP32
2. **USB cable** for ESP32 connection
3. **Required libraries:**
   - `ssd1306.py` - OLED display driver
   - Standard MicroPython libraries (included)

### Step-by-Step Installation

#### 1. Install MicroPython
```bash
# Flash MicroPython firmware to ESP32
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-micropython.bin
```

#### 2. Upload Required Files
Upload these files to your ESP32:
- `ssd1306.py` (OLED driver)
- `main.py` (this game)

**Using ampy:**
```bash
ampy --port /dev/ttyUSB0 put ssd1306.py
ampy --port /dev/ttyUSB0 put main.py
```

**Using Thonny IDE:**
1. Open Thonny
2. Connect to ESP32
3. Right-click → Upload to /
4. Select `ssd1306.py` and `main.py`

#### 3. Run the Game
```python
# In MicroPython REPL:
import main
main.main()
```

Or set it to auto-run on boot:
```python
# Create boot.py on ESP32:
import main
main.main()
```

---

## 🎮 How to Play

### Controls
| Action | Control |
|--------|---------|
| **Move** | Automatic (left ↔ right) |
| **Shoot** | Press button |

### Objective
🎯 **Destroy all 50 invaders before they reach the bottom!**

### Scoring
- Each invader destroyed: **+10 points**
- Total possible score: **500 points**

---

## 🎯 Game Mechanics

### Player Ship
- Moves automatically at constant speed
- Reverses direction at screen edges
- Can fire one missile at a time
- Position: Bottom of screen

### Invaders
- **Formation:** 5 rows × 10 columns
- **Movement:** Horizontal sweep with downward drops
- **Speed:** Increases as invaders are eliminated
  - < 30 alive: Speed +1
  - < 15 alive: Speed +2
  - < 5 alive: Speed +3

### Missile System
- **Speed:** 3 pixels per frame
- **Limit:** One active missile at a time
- **Range:** Full screen height
- **Collision:** Destroys one invader per hit

### Win/Lose Conditions
| Condition | Result |
|-----------|--------|
| All invaders destroyed | 🏆 **YOU WIN!** |
| Invaders reach player level | ☠️ **GAME OVER** |

---

## ⚙️ Configuration

### Display Settings
```python
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
```

### Player Settings
```python
PLAYER_AUTO_MOVE_SPEED = 2  # Movement speed (1-5)
PLAYER_Y = 56               # Vertical position
```

### Missile Settings
```python
MISSILE_SPEED = 3    # Missile velocity (1-5)
MISSILE_WIDTH = 3    # Missile width in pixels
MISSILE_HEIGHT = 6   # Missile height in pixels
```

### Invader Settings
```python
INVADER_ROWS = 5            # Number of rows (1-8)
INVADER_COLS = 10           # Number of columns (1-12)
INVADER_MOVE_SPEED = 1      # Movement speed
INVADER_DROP_AMOUNT = 4     # Vertical drop distance
```

### Audio Settings
```python
BUZZER_PIN = 25        # PWM buzzer pin
SOUND_SHOOT = 1000     # Shoot frequency (Hz)
SOUND_HIT = 800        # Hit frequency (Hz)
SOUND_WIN = 1200       # Victory frequency (Hz)
SOUND_LOSE = 400       # Game over frequency (Hz)
```

### Game Settings
```python
FPS = 30               # Frames per second (15-60)
```

---

## 🐛 Troubleshooting

### Display Issues
**Problem:** Nothing shows on OLED
```python
# Check I2C connection
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
print(i2c.scan())  # Should show [60] or [0x3c]
```

**Solution:**
- Verify wiring (SCL=22, SDA=21)
- Check power supply (3.3V)
- Try changing I2C address in code

### Button Not Working
**Problem:** Can't shoot

**Solution:**
- Check button connection to GPIO 4
- Test button directly:
```python
from machine import Pin
btn = Pin(4, Pin.IN, Pin.PULL_UP)
print(btn.value())  # Should be 1, and 0 when pressed
```

### No Sound
**Problem:** Buzzer silent

**Solution:**
- Verify buzzer polarity
- Check GPIO 25 connection
- Test buzzer:
```python
from machine import Pin, PWM
buzzer = PWM(Pin(25), freq=1000, duty=512)
```

### Game Too Fast/Slow
**Problem:** Gameplay speed issues

**Solution:**
```python
# Adjust in settings:
FPS = 20  # Slower game
FPS = 40  # Faster game
```

### Memory Errors
**Problem:** `MemoryError` or crashes

**Solution:**
```python
# Add to main loop (already included):
import gc
gc.collect()  # Force garbage collection
```

---

## 🎨 Customization Ideas

### Easy Mode
```python
INVADER_ROWS = 3           # Fewer invaders
INVADER_COLS = 8
PLAYER_AUTO_MOVE_SPEED = 1 # Slower movement
```

### Hard Mode
```python
INVADER_ROWS = 6           # More invaders
INVADER_COLS = 12
MISSILE_SPEED = 2          # Slower missiles
PLAYER_AUTO_MOVE_SPEED = 3 # Faster movement
```

### Speed Run Mode
```python
FPS = 60                   # Maximum frame rate
INVADER_MOVE_SPEED = 2     # Fast invaders
```

---

## 🔧 Technical Details

### Performance
- **Frame Rate:** 30 FPS
- **Memory Usage:** ~15KB RAM
- **Display Refresh:** I2C @ 400kHz
- **Input Latency:** <33ms

### Display Coordinates
```
(0,0) ─────────────── (127,0)
  │                      │
  │    GAME AREA        │
  │                      │
(0,63) ─────────────── (127,63)
```

### Collision Detection
Uses AABB (Axis-Aligned Bounding Box) algorithm:
```python
if (missile.x < invader.x + width and
    missile.x + missile_width > invader.x and
    missile.y < invader.y + height and
    missile.y + missile_height > invader.y):
    # Collision detected!
```

---

**Enjoy the game! 🚀👾**

---