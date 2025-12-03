"""
Space Invaders Pro - Single File Version
"""

from machine import Pin, PWM, I2C
from ssd1306 import SSD1306_I2C
import time
import gc

# ==================== SETTINGS ====================
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# Player settings
PLAYER_START_X = 60
PLAYER_Y = 56
PLAYER_WIDTH = 8
PLAYER_HEIGHT = 6
PLAYER_AUTO_MOVE_SPEED = 2  # Auto movement speed

# Missile settings
MISSILE_SPEED = 3
MISSILE_WIDTH = 3
MISSILE_HEIGHT = 6

# Invader settings
INVADER_ROWS = 5
INVADER_COLS = 10
INVADER_WIDTH = 8
INVADER_HEIGHT = 6
INVADER_START_X = 8
INVADER_START_Y = 4
INVADER_SPACING_X = 4
INVADER_SPACING_Y = 2
INVADER_MOVE_SPEED = 1
INVADER_DROP_AMOUNT = 4

# Controls
BUTTON_PIN = 4

# Audio
BUZZER_PIN = 25
SOUND_SHOOT = 1000
SOUND_HIT = 800
SOUND_WIN = 1200
SOUND_LOSE = 400

# Game settings
FPS = 30


# ==================== AUDIO MANAGER ====================
class AudioManager:
    def __init__(self):
        try:
            self.buzzer = PWM(Pin(BUZZER_PIN), freq=1000, duty=0)
            self.enabled = True
        except:
            self.enabled = False
    
    def play_tone(self, frequency, duration_ms):
        if not self.enabled:
            return
        try:
            self.buzzer.freq(frequency)
            self.buzzer.duty(512)
            time.sleep_ms(duration_ms)
            self.buzzer.duty(0)
        except:
            pass
    
    def shoot(self):
        self.play_tone(SOUND_SHOOT, 50)
    
    def hit(self):
        self.play_tone(SOUND_HIT, 100)
    
    def win(self):
        for freq in [800, 1000, 1200]:
            self.play_tone(freq, 150)
    
    def lose(self):
        for freq in [600, 400, 200]:
            self.play_tone(freq, 200)


# ==================== MISSILE ====================
class Missile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
    
    def update(self):
        if not self.active:
            return
        
        self.y -= MISSILE_SPEED
        
        if self.y < -MISSILE_HEIGHT:
            self.active = False
    
    def draw(self, display):
        if self.active:
            display.fill_rect(self.x, self.y, MISSILE_WIDTH, MISSILE_HEIGHT, 1)


# ==================== PLAYER ====================
class Player:
    def __init__(self, audio_manager):
        self.x = PLAYER_START_X
        self.y = PLAYER_Y
        self.direction = 1  # 1 = right, -1 = left
        self.missile = None
        self.audio = audio_manager
    
    def auto_move(self):
        """Automatic left-right movement"""
        self.x += self.direction * PLAYER_AUTO_MOVE_SPEED
        
        # Check boundaries and reverse direction
        if self.x <= 0:
            self.x = 0
            self.direction = 1
        elif self.x >= SCREEN_WIDTH - PLAYER_WIDTH:
            self.x = SCREEN_WIDTH - PLAYER_WIDTH
            self.direction = -1
    
    def shoot(self):
        """Fire missile - only if no active missile exists"""
        if self.missile is None or not self.missile.active:
            missile_x = self.x + PLAYER_WIDTH // 2 - MISSILE_WIDTH // 2
            missile_y = self.y - MISSILE_HEIGHT - 2
            self.missile = Missile(missile_x, missile_y)
            self.audio.shoot()
            return True
        return False
    
    def update(self):
        """Update movement and missile"""
        self.auto_move()  # Automatic movement
        
        if self.missile and self.missile.active:
            self.missile.update()
    
    def draw(self, display):
        # Draw spaceship (triangle)
        display.fill_rect(self.x + 3, self.y, 2, 2, 1)
        display.fill_rect(self.x + 1, self.y + 2, 6, 2, 1)
        display.fill_rect(self.x, self.y + 4, 8, 2, 1)
        
        # Draw missile
        if self.missile and self.missile.active:
            self.missile.draw(display)


# ==================== INVADER ====================
class Invader:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
    
    def draw(self, display):
        if self.alive:
            display.fill_rect(self.x + 1, self.y, 6, 2, 1)
            display.fill_rect(self.x, self.y + 2, 8, 2, 1)
            display.fill_rect(self.x + 1, self.y + 4, 6, 2, 1)


class InvaderFormation:
    def __init__(self, audio_manager):
        self.invaders = []
        self.direction = 1
        self.move_counter = 0
        self.speed_increase = 0
        self.audio = audio_manager
        
        for row in range(INVADER_ROWS):
            for col in range(INVADER_COLS):
                x = INVADER_START_X + col * (INVADER_WIDTH + INVADER_SPACING_X)
                y = INVADER_START_Y + row * (INVADER_HEIGHT + INVADER_SPACING_Y)
                self.invaders.append(Invader(x, y))
    
    def count_alive(self):
        return sum(1 for inv in self.invaders if inv.alive)
    
    def update(self):
        self.move_counter += 1
        move_delay = max(5, 15 - self.speed_increase)
        
        if self.move_counter >= move_delay:
            self.move_counter = 0
            self.move()
    
    def move(self):
        should_drop = False
        
        for invader in self.invaders:
            if not invader.alive:
                continue
            
            invader.x += self.direction * INVADER_MOVE_SPEED
            
            if invader.x <= 0 or invader.x >= SCREEN_WIDTH - INVADER_WIDTH:
                should_drop = True
        
        if should_drop:
            self.direction *= -1
            for invader in self.invaders:
                if invader.alive:
                    invader.y += INVADER_DROP_AMOUNT
    
    def check_collision(self, missile):
        if not missile or not missile.active:
            return False
        
        for invader in self.invaders:
            if not invader.alive:
                continue
            
            if (missile.x < invader.x + INVADER_WIDTH and
                missile.x + MISSILE_WIDTH > invader.x and
                missile.y < invader.y + INVADER_HEIGHT and
                missile.y + MISSILE_HEIGHT > invader.y):
                
                invader.alive = False
                missile.active = False
                self.audio.hit()
                
                alive_count = self.count_alive()
                if alive_count < 30:
                    self.speed_increase = 1
                if alive_count < 15:
                    self.speed_increase = 2
                if alive_count < 5:
                    self.speed_increase = 3
                
                return True
        
        return False
    
    def reached_bottom(self):
        for invader in self.invaders:
            if invader.alive and invader.y >= PLAYER_Y - INVADER_HEIGHT:
                return True
        return False
    
    def draw(self, display):
        for invader in self.invaders:
            invader.draw(display)


# ==================== SCORE MANAGER ====================
class ScoreManager:
    def __init__(self):
        self.score = 0
        self.high_score = 0
    
    def add_points(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
    
    def reset(self):
        self.score = 0
    
    def get_score(self):
        return self.score
    
    def get_high_score(self):
        return self.high_score


# ==================== BUTTON MANAGER ====================
class ButtonManager:
    def __init__(self):
        self.button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        self.last_state = 1
    
    def is_pressed(self):
        """Check if button is pressed (new press detected)"""
        current_state = self.button.value()
        
        # Press = transition from 1 (not pressed) to 0 (pressed)
        if current_state == 0 and self.last_state == 1:
            self.last_state = current_state
            return True
        
        self.last_state = current_state
        return False


# ==================== GAME ====================
class Game:
    def __init__(self):
        print("Initializing hardware...")
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.display = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, self.i2c)
        
        self.audio = AudioManager()
        self.button_manager = ButtonManager()
        self.score_manager = ScoreManager()
        
        self.player = Player(self.audio)
        self.formation = InvaderFormation(self.audio)
        
        self.running = True
        self.game_over = False
        self.won = False
        
        print("Game initialized!")
    
    def handle_input(self):
        """Check button press for shooting only"""
        if self.button_manager.is_pressed():
            self.player.shoot()
    
    def update(self):
        if self.game_over:
            return
        
        self.player.update()  # automatic movement
        self.formation.update()
        
        if self.formation.check_collision(self.player.missile):
            self.score_manager.add_points(10)
        
        if self.formation.count_alive() == 0:
            self.game_over = True
            self.won = True
            self.audio.win()
        
        if self.formation.reached_bottom():
            self.game_over = True
            self.won = False
            self.audio.lose()
    
    def draw(self):
        self.display.fill(0)
        
        if not self.game_over:
            self.player.draw(self.display)
            self.formation.draw(self.display)
            
            score_text = f"{self.score_manager.get_score()}"
            self.display.text(score_text, 0, 0, 1)
        else:
            if self.won:
                self.display.text("YOU WIN!", 35, 20, 1)
            else:
                self.display.text("GAME OVER", 25, 20, 1)
            
            score_text = f"Score: {self.score_manager.get_score()}"
            self.display.text(score_text, 20, 35, 1)
        
        self.display.show()
    
    def run(self):
        frame_time = 1000 // FPS
        
        while self.running:
            frame_start = time.ticks_ms()
            
            self.handle_input()
            self.update()
            self.draw()
            
            if self.game_over:
                time.sleep(3)
                break
            
            elapsed = time.ticks_diff(time.ticks_ms(), frame_start)
            if elapsed < frame_time:
                time.sleep_ms(frame_time - elapsed)
            
            gc.collect()
    
    def cleanup(self):
        self.display.fill(0)
        self.display.show()


# ==================== MAIN ====================
def main():
    print("=" * 40)
    print("  SPACE INVADERS PRO")
    print("  ESP32 Single-Button Edition")
    print("=" * 40)
    print()
    print("Controls:")
    print("  Auto-Move: Player moves automatically")
    print("  Button: SHOOT!")
    print()
    print("Starting game...")
    print("=" * 40)
    
    try:
        game = Game()
        game.run()
        game.cleanup()
        
        print()
        print("=" * 40)
        print(f"Final Score: {game.score_manager.get_score()}")
        print(f"High Score:  {game.score_manager.get_high_score()}")
        print("=" * 40)
        print("Game Over!")
        
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import sys
        sys.print_exception(e)


if __name__ == "__main__":
    main()