import pygame  # Import Pygame library for game development
import random  # Import random module for randomizing collectibles and enemy actions

# Initialize Pygame for graphics, events, and sound
pygame.init()  # Initialize all Pygame modules
pygame.mixer.init()  # Initialize Pygame's sound mixer for audio playback

# Screen settings
SCREEN_WIDTH = 800  # Define screen width as 800 pixels
SCREEN_HEIGHT = 600  # Define screen height as 600 pixels
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Create game window with specified dimensions
pygame.display.set_caption("Tank Battle: Side-Scroller")  # Set the window title to "Tank Battle: Side-Scroller"

# Colors (RGB and RGBA for transparency)
WHITE = (255, 255, 255)  # Define white color as RGB (255, 255, 255)
BLACK = (0, 0, 0)  # Define black color as RGB (0, 0, 0)
PLAYER_COLOR = (50, 168, 82)  # Define green color for player tank as RGB (50, 168, 82)
ENEMY_COLOR = (200, 50, 50)  # Define red color for enemy tanks as RGB (200, 50, 50)
BOSS_COLOR = (50, 50, 200)  # Define blue color for boss tank as RGB (50, 50, 200)
PROJECTILE_COLOR = (255, 255, 100)  # Define yellow color for projectiles as RGB (255, 255, 100)
HEALTH_COLOR = (100, 255, 100)  # Define bright green color for health collectible as RGB (100, 255, 100)
LIFE_COLOR = (100, 100, 255)  # Define blue color for life collectible as RGB (100, 100, 255)
SCORE_COLOR = (255, 215, 0)  # Define gold color for score collectible as RGB (255, 215, 0)
GROUND_COLOR = (139, 69, 19)  # Define brown color for ground as RGB (139, 69, 19)
UI_BG_COLOR = (0, 0, 0, 150)  # Define semi-transparent black for UI background as RGBA (0, 0, 0, 150)

# Game settings
GRAVITY = 0.8  # Set gravity constant for player jumping to 0.8 pixels per frame squared
GROUND_HEIGHT = SCREEN_HEIGHT - 50  # Set ground position 50 pixels from the bottom of the screen
LEVEL_WIDTHS = [3000, 4500, 6000]  # Define widths for three levels as 3000, 4500, 6000 pixels (customizable)
LEVEL_GRADIENTS = [  # Define gradient colors for level backgrounds
    [(70, 70, 130), (120, 120, 180)],  # Set blue-gray gradient for level 1 (top: 70,70,130; bottom: 120,120,180)
    [(130, 70, 70), (180, 120, 120)],  # Set red-brown gradient for level 2 (top: 130,70,70; bottom: 180,120,120)
    [(70, 130, 70), (120, 180, 120)]   # Set green gradient for level 3 (top: 70,130,70; bottom: 120,180,120)
]

# Load sound effects (place .wav files in the same directory as this script)
try:  # Begin try block to handle potential file loading errors
    SHOOT_SOUND = pygame.mixer.Sound("shoot.wav")  # Load shooting sound effect from shoot.wav
    COLLECT_SOUND = pygame.mixer.Sound("collect.wav")  # Load collectible pickup sound from collect.wav
    DAMAGE_SOUND = pygame.mixer.Sound("damage.wav")  # Load damage sound effect from damage.wav
except FileNotFoundError:  # Catch FileNotFoundError if sound files are missing
    print("Sound files not found. Please add shoot.wav, collect.wav, and damage.wav to the game directory.")  # Print warning if sound files are not found
    SHOOT_SOUND = COLLECT_SOUND = DAMAGE_SOUND = None  # Set sound variables to None to disable sound if files are missing

# Player class to manage tank movement, health, lives, and score
class Player:  # Define Player class for the controllable tank
    def __init__(self, x, y):  # Initialize player with starting position (x, y)
        self.rect = pygame.Rect(x, y, 40, 30)  # Create player hitbox as a 40x30 rectangle at (x, y)
        self.vx = 0  # Set initial horizontal velocity to 0
        self.vy = 0  # Set initial vertical velocity to 0
        self.speed = 5  # Set movement speed to 5 pixels per frame
        self.jump_power = -15  # Set jump strength to -15 pixels per frame
        self.health = 100  # Set initial health to 100
        self.max_health = 100  # Set maximum health to 100
        self.lives = 3  # Set initial number of lives to 3
        self.on_ground = False  # Set initial grounded state to False
        self.score = 0  # Set initial player score to 0

    def move(self, keys, level_width):  # Define method to update player movement
        self.vx = 0  # Reset horizontal velocity to 0
        if keys[pygame.K_LEFT] and self.rect.left > 0:  # Check if left arrow is pressed and player is not at left edge
            self.vx = -self.speed  # Set horizontal velocity to move left
        if keys[pygame.K_RIGHT] and self.rect.right < level_width:  # Check if right arrow is pressed and player is not at right edge
            self.vx = self.speed  # Set horizontal velocity to move right
        if keys[pygame.K_SPACE] and self.on_ground:  # Check if space key is pressed and player is on ground
            self.vy = self.jump_power  # Apply jump velocity
            self.on_ground = False  # Set grounded state to False

        self.vy += GRAVITY  # Apply gravity to vertical velocity
        self.rect.x += self.vx  # Update x position based on horizontal velocity
        self.rect.y += self.vy  # Update y position based on vertical velocity

        if self.rect.bottom >= GROUND_HEIGHT:  # Check if player is below or at ground level
            self.rect.bottom = GROUND_HEIGHT  # Snap player to ground level
            self.vy = 0  # Reset vertical velocity to 0
            self.on_ground = True  # Set grounded state to True

    def take_damage(self, damage):  # Define method to apply damage to player
        self.health -= damage  # Reduce health by damage amount
        if DAMAGE_SOUND:  # Check if damage sound is available
            DAMAGE_SOUND.play()  # Play damage sound effect
        if self.health <= 0:  # Check if health is depleted
            self.lives -= 1  # Decrease lives by 1
            self.health = self.max_health  # Reset health to maximum
            self.rect.x = 100  # Reset x position to 100
            self.rect.y = GROUND_HEIGHT - 30  # Reset y position to just above ground
        return self.lives > 0  # Return True if player still has lives

    def draw(self, screen, camera):  # Define method to draw player
        rect = camera.apply(self.rect)  # Apply camera offset to player position
        pygame.draw.rect(screen, PLAYER_COLOR, rect)  # Draw player tank body as a colored rectangle
        turret_center = (rect.centerx, rect.centery - 10)  # Calculate center of turret above tank
        pygame.draw.circle(screen, BLACK, turret_center, 8)  # Draw black turret circle
        health_width = (self.health / self.max_health) * 40  # Calculate health bar width proportional to health
        pygame.draw.rect(screen, BLACK, (rect.x, rect.y - 15, 40, 5))  # Draw black background for health bar
        pygame.draw.rect(screen, HEALTH_COLOR, (rect.x, rect.y - 15, health_width, 5))  # Draw green health bar

# Projectile class for player and enemy shots
class Projectile:  # Define Projectile class for shots fired
    def __init__(self, x, y, direction, damage=10):  # Initialize projectile with position, direction, and damage
        self.rect = pygame.Rect(x, y, 10, 5)  # Create projectile hitbox as a 10x5 rectangle
        self.vx = direction * 15  # Set horizontal speed based on direction (15 pixels per frame)
        self.damage = damage  # Set damage value for the projectile
        if SHOOT_SOUND:  # Check if shoot sound is available
            SHOOT_SOUND.play()  # Play shoot sound effect

    def move(self):  # Define method to update projectile position
        self.rect.x += self.vx  # Move projectile horizontally based on velocity

    def draw(self, screen, camera):  # Define method to draw projectile
        rect = camera.apply(self.rect)  # Apply camera offset to projectile position
        pygame.draw.rect(screen, PROJECTILE_COLOR, rect)  # Draw projectile body as a yellow rectangle
        pygame.draw.circle(screen, WHITE, (rect.centerx, rect.centery), 3)  # Draw white glow circle at center

# Enemy class for regular enemies and boss
class Enemy:  # Define Enemy class for opponent tanks
    def __init__(self, x, y, is_boss=False):  # Initialize enemy with position and boss status
        self.rect = pygame.Rect(x, y, 50 if is_boss else 40, 30)  # Create hitbox (50x30 for boss, 40x30 for regular)
        self.vx = -2  # Set initial horizontal speed to -2 pixels per frame
        self.health = 50 if is_boss else 20  # Set health to 50 for boss, 20 for regular
        self.max_health = self.health  # Set maximum health equal to initial health
        self.is_boss = is_boss  # Store whether enemy is a boss
        self.shoot_timer = 0  # Initialize timer for shooting
        self.shoot_interval = 60 if is_boss else 120  # Set shooting interval (60 frames for boss, 120 for regular)

    def move(self, player, level_width):  # Define method to update enemy movement
        if not self.is_boss:  # Check if enemy is not a boss
            if self.rect.x < 0 or self.rect.x > level_width - self.rect.width:  # Check if enemy hits level boundaries
                self.vx = -self.vx  # Reverse direction at edges
            self.rect.x += self.vx  # Update x position based on velocity
        else:  # Handle boss movement
            if player.rect.x > self.rect.x:  # Check if player is to the right of boss
                self.vx = 1  # Move boss right
            elif player.rect.x < self.rect.x:  # Check if player is to the left of boss
                self.vx = -1  # Move boss left
            else:  # Check if player is aligned with boss
                self.vx = 0  # Stop boss movement
            self.rect.x += self.vx  # Update x position based on velocity

    def shoot(self, projectiles):  # Define method for enemy shooting
        self.shoot_timer += 1  # Increment shooting timer
        if self.shoot_timer >= self.shoot_interval:  # Check if enough time has passed to shoot
            direction = -1 if self.vx < 0 else 1  # Set projectile direction based on enemy movement
            projectiles.append(Projectile(self.rect.centerx, self.rect.centery, direction, 15 if self.is_boss else 5))  # Add projectile with appropriate damage
            self.shoot_timer = 0  # Reset shooting timer

    def take_damage(self, damage):  # Define method to apply damage to enemy
        self.health -= damage  # Reduce health by damage amount
        if DAMAGE_SOUND:  # Check if damage sound is available
            DAMAGE_SOUND.play()  # Play damage sound effect
        return self.health > 0  # Return True if enemy is still alive

    def draw(self, screen, camera):  # Define method to draw enemy
        color = BOSS_COLOR if self.is_boss else ENEMY_COLOR  # Choose blue for boss, red for regular enemy
        rect = camera.apply(self.rect)  # Apply camera offset to enemy position
        pygame.draw.rect(screen, color, rect)  # Draw enemy tank body as a colored rectangle
        turret_center = (rect.centerx, rect.centery - 10)  # Calculate center of turret above tank
        pygame.draw.circle(screen, BLACK, turret_center, 10 if self.is_boss else 8)  # Draw black turret circle (larger for boss)
        health_width = (self.health / self.max_health) * self.rect.width  # Calculate health bar width proportional to health
        pygame.draw.rect(screen, BLACK, (rect.x, rect.y - 15, self.rect.width, 5))  # Draw black background for health bar
        pygame.draw.rect(screen, HEALTH_COLOR, (rect.x, rect.y - 15, health_width, 5))  # Draw green health bar

# Collectible class for power-ups
class Collectible:  # Define Collectible class for game power-ups
    def __init__(self, x, y, type_):  # Initialize collectible with position and type
        self.rect = pygame.Rect(x, y, 20, 20)  # Create collectible hitbox as a 20x20 rectangle
        self.type = type_  # Store collectible type ("health", "life", "score")

    def apply(self, player):  # Define method to apply collectible effects
        if self.type == "health":  # Check if collectible is health type
            player.health = min(player.health + 20, player.max_health)  # Increase player health by 20, up to max
            player.score += 50  # Add 50 points to player score
        elif self.type == "life":  # Check if collectible is life type
            player.lives += 1  # Increase player lives by 1
            player.score += 100  # Add 100 points to player score
        elif self.type == "score":  # Check if collectible is score type
            player.score += 200  # Add 200 points to player score
        if COLLECT_SOUND:  # Check if collect sound is available
            COLLECT_SOUND.play()  # Play collect sound effect

    def draw(self, screen, camera):  # Define method to draw collectible
        rect = camera.apply(self.rect)  # Apply camera offset to collectible position
        color = {"health": HEALTH_COLOR, "life": LIFE_COLOR, "score": SCORE_COLOR}[self.type]  # Choose color based on collectible type
        if self.type == "health":  # Check if collectible is health type
            pygame.draw.circle(screen, color, rect.center, 10)  # Draw green circle for health collectible
        elif self.type == "life":  # Check if collectible is life type
            points = [(rect.centerx, rect.y), (rect.centerx + 5, rect.centery + 10),  # Define points for star polygon
                      (rect.centerx + 15, rect.centery + 10), (rect.centerx + 5, rect.centery + 15),
                      (rect.centerx + 10, rect.bottom), (rect.centerx, rect.centery + 15),
                      (rect.centerx - 10, rect.centery + 15), (rect.centerx - 5, rect.centery + 10),
                      (rect.centerx - 15, rect.centery + 10), (rect.centerx - 5, rect.y)]
            pygame.draw.polygon(screen, color, points)  # Draw blue star for life collectible
        else:  # Handle score collectible
            points = [(rect.centerx, rect.y), (rect.right, rect.centery),  # Define points for diamond polygon
                      (rect.centerx, rect.bottom), (rect.left, rect.centery)]
            pygame.draw.polygon(screen, color, points)  # Draw gold diamond for score collectible

# Camera class for smooth player tracking
class Camera:  # Define Camera class for dynamic view
    def __init__(self, level_width):  # Initialize camera with level width
        self.offset = 0  # Set initial camera offset to 0
        self.level_width = level_width  # Store level width for boundary calculations

    def update(self, player):  # Define method to update camera position
        target_x = player.rect.centerx - SCREEN_WIDTH // 2  # Calculate target x position to center player
        self.offset = max(0, min(target_x, self.level_width - SCREEN_WIDTH))  # Clamp offset to level boundaries

    def apply(self, rect):  # Define method to apply camera offset
        return rect.move(-self.offset, 0)  # Move rectangle by negative offset to simulate camera movement

# Draw gradient background for levels and overlays
def draw_gradient(screen, top_color, bottom_color):  # Define function to draw gradient background
    for y in range(SCREEN_HEIGHT):  # Iterate over each vertical pixel
        ratio = y / SCREEN_HEIGHT  # Calculate interpolation ratio based on y position
        color = (  # Calculate interpolated color for current y
            int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio),  # Interpolate red component
            int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio),  # Interpolate green component
            int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)   # Interpolate blue component
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))  # Draw horizontal line with interpolated color

# Create level with enemies and collectibles
def create_level(level_num, level_width):  # Define function to create level content
    enemies = []  # Initialize empty list for enemies
    collectibles = []  # Initialize empty list for collectibles
    
    if level_num == 0:  # Check if creating level 1
        num_enemies = 5  # Set number of enemies to 5
        num_collectibles = 6  # Set number of collectibles to 6
        for i in range(num_enemies):  # Iterate to create enemies
            enemies.append(Enemy(500 + i * (level_width // num_enemies), GROUND_HEIGHT - 30))  # Add enemy spaced by level width
            if i < num_collectibles - 1:  # Add collectibles for all but last
                collectibles.append(Collectible(400 + i * (level_width // num_collectibles), GROUND_HEIGHT - 20, random.choice(["health", "score"])))  # Add random health or score collectible
        collectibles.append(Collectible(800, GROUND_HEIGHT - 20, "life"))  # Add extra life collectible
    elif level_num == 1:  # Check if creating level 2
        num_enemies = 7  # Set number of enemies to 7
        num_collectibles = 7  # Set number of collectibles to 7
        for i in range(num_enemies):  # Iterate to create enemies
            enemies.append(Enemy(600 + i * (level_width // num_enemies), GROUND_HEIGHT - 30))  # Add enemy spaced by level width
            collectibles.append(Collectible(500 + i * (level_width // num_collectibles), GROUND_HEIGHT - 20, random.choice(["health", "life", "score"])))  # Add random collectible
    elif level_num == 2:  # Check if creating level 3
        num_enemies = 3  # Set number of regular enemies to 3
        num_collectibles = 4  # Set number of collectibles to 4
        enemies.append(Enemy(level_width - 200, GROUND_HEIGHT - 30, is_boss=True))  # Add boss enemy near level end
        for i in range(num_enemies):  # Iterate to create regular enemies
            enemies.append(Enemy(600 + i * (level_width // (num_enemies + 1)), GROUND_HEIGHT - 30))  # Add regular enemy spaced by level width
            collectibles.append(Collectible(500 + i * (level_width // num_collectibles), GROUND_HEIGHT - 20, random.choice(["health", "life"])))  # Add random health or life collectible
        collectibles.append(Collectible(1000, GROUND_HEIGHT - 20, "life"))  # Add extra life collectible
    
    return enemies, collectibles, level_width  # Return enemies, collectibles, and level width

# Main game function
def main():  # Define main game function
    player = Player(100, GROUND_HEIGHT - 30)  # Create player at starting position
    projectiles = []  # Initialize empty list for player projectiles
    enemy_projectiles = []  # Initialize empty list for enemy projectiles
    current_level = 0  # Set initial level to 0 (level 1)
    enemies, collectibles, level_width = create_level(current_level, LEVEL_WIDTHS[current_level])  # Create initial level content
    camera = Camera(level_width)  # Initialize camera with level width
    game_over = False  # Set initial game over state to False
    win = False  # Set initial win state to False for final congratulation
    level_complete = False  # Set initial level complete state to False
    level_complete_timer = 0  # Initialize timer for level complete message
    font = pygame.font.SysFont("arial", 24, bold=True)  # Create font for UI text (24pt, bold)
    congrats_font = pygame.font.SysFont("arial", 36, bold=True)  # Create larger font for final congratulation (36pt, bold)
    clock = pygame.time.Clock()  # Create clock for controlling frame rate

    instruction_texts = [  # Create list of instruction text surfaces
        font.render("Controls:", True, WHITE),  # Render "Controls:" text in white
        font.render("Left/Right: Move", True, WHITE),  # Render "Left/Right: Move" text in white
        font.render("Space: Jump", True, WHITE),  # Render "Space: Jump" text in white
        font.render("S: Shoot", True, WHITE),  # Render "S: Shoot" text in white
        font.render("R: Restart", True, WHITE)  # Render "R: Restart" text in white
    ]

    while True:  # Start infinite game loop
        for event in pygame.event.get():  # Iterate over all Pygame events
            if event.type == pygame.QUIT:  # Check if window close button is clicked
                pygame.quit()  # Quit Pygame
                return  # Exit the main function
            if event.type == pygame.KEYDOWN:  # Check if a key is pressed
                if event.key == pygame.K_r and (game_over or win):  # Check if 'R' is pressed during game over or final win
                    player = Player(100, GROUND_HEIGHT - 30)  # Reset player to starting position
                    current_level = 0  # Reset to level 1
                    enemies, collectibles, level_width = create_level(current_level, LEVEL_WIDTHS[current_level])  # Recreate level content
                    camera = Camera(level_width)  # Reset camera with new level width
                    projectiles.clear()  # Clear all player projectiles
                    enemy_projectiles.clear()  # Clear all enemy projectiles
                    game_over = False  # Reset game over state
                    win = False  # Reset final win state
                    level_complete = False  # Reset level complete state
                    level_complete_timer = 0  # Reset level complete timer
                if event.key == pygame.K_s and not (game_over or win or level_complete):  # Check if 'S' is pressed and game is active
                    projectiles.append(Projectile(player.rect.centerx, player.rect.centery, 1))  # Add new player projectile

        if not (game_over or win or level_complete):  # Check if game is active (not game over, won, or level complete)
            keys = pygame.key.get_pressed()  # Get current state of all keyboard keys
            player.move(keys, level_width)  # Update player movement based on key input
            camera.update(player)  # Update camera to follow player

            for p in projectiles[:]:  # Iterate over copy of player projectiles
                p.move()  # Move projectile
                if p.rect.x > level_width or p.rect.x < 0:  # Check if projectile is out of level bounds
                    projectiles.remove(p)  # Remove projectile from list
                else:  # Handle projectile collisions
                    for enemy in enemies[:]:  # Iterate over copy of enemies
                        if p.rect.colliderect(enemy.rect):  # Check if projectile hits enemy
                            if not enemy.take_damage(p.damage):  # Apply damage and check if enemy is defeated
                                enemies.remove(enemy)  # Remove defeated enemy
                                player.score += 100 if not enemy.is_boss else 500  # Add 100 points for regular, 500 for boss
                            projectiles.remove(p)  # Remove projectile
                            break  # Exit enemy loop after hit

            for enemy in enemies:  # Iterate over enemies
                enemy.move(player, level_width)  # Update enemy movement
                if random.random() < 0.02:  # Check if enemy should shoot (2% chance per frame)
                    enemy.shoot(enemy_projectiles)  # Make enemy shoot
                if enemy.rect.colliderect(player.rect):  # Check if enemy collides with player
                    if not player.take_damage(10):  # Apply 10 damage to player and check if alive
                        game_over = True  # Set game over state if player dies

            for p in enemy_projectiles[:]:  # Iterate over copy of enemy projectiles
                p.move()  # Move projectile
                if p.rect.colliderect(player.rect):  # Check if projectile hits player
                    if not player.take_damage(p.damage):  # Apply damage and check if player dies
                        game_over = True  # Set game over state
                    enemy_projectiles.remove(p)  # Remove projectile
                elif p.rect.x > level_width or p.rect.x < 0:  # Check if projectile is out of bounds
                    enemy_projectiles.remove(p)  # Remove projectile

            for c in collectibles[:]:  # Iterate over copy of collectibles
                if player.rect.colliderect(c.rect):  # Check if player collects item
                    c.apply(player)  # Apply collectible effect to player
                    collectibles.remove(c)  # Remove collected item

            if not enemies:  # Check if all enemies are defeated
                if current_level < 2:  # Check if not on last level
                    level_complete = True  # Set level complete state
                    level_complete_timer = pygame.time.get_ticks()  # Record time of level completion
                else:  # Handle last level completion
                    win = True  # Trigger final win state

        if level_complete:  # Check if level is complete
            if pygame.time.get_ticks() - level_complete_timer > 2000:  # Check if 2 seconds have passed
                current_level += 1  # Advance to next level
                enemies, collectibles, level_width = create_level(current_level, LEVEL_WIDTHS[current_level])  # Create new level content
                camera = Camera(level_width)  # Update camera for new level
                player.rect.x = 100  # Reset player x position
                player.rect.y = GROUND_HEIGHT - 30  # Reset player y position
                level_complete = False  # Reset level complete state
                level_complete_timer = 0  # Reset level complete timer

        draw_gradient(screen, LEVEL_GRADIENTS[current_level][0], LEVEL_GRADIENTS[current_level][1])  # Draw level background gradient
        
        pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))  # Draw brown ground rectangle
        for x in range(0, SCREEN_WIDTH, 20):  # Iterate over screen width in steps of 20
            pygame.draw.line(screen, (100, 50, 0), (x, GROUND_HEIGHT), (x + 10, SCREEN_HEIGHT), 2)  # Draw diagonal texture lines

        player.draw(screen, camera)  # Draw player tank
        for p in projectiles:  # Iterate over player projectiles
            p.draw(screen, camera)  # Draw each projectile
        for p in enemy_projectiles:  # Iterate over enemy projectiles
            p.draw(screen, camera)  # Draw each projectile
        for enemy in enemies:  # Iterate over enemies
            enemy.draw(screen, camera)  # Draw each enemy
        for c in collectibles:  # Iterate over collectibles
            c.draw(screen, camera)  # Draw each collectible

        ui_rect = pygame.Rect(10, 10, 200, 100)  # Create rectangle for UI panel
        pygame.draw.rect(screen, UI_BG_COLOR, ui_rect)  # Draw semi-transparent UI background
        score_text = font.render(f"Score: {player.score}", True, WHITE)  # Render score text
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)  # Render lives text
        level_text = font.render(f"Level: {current_level + 1}", True, WHITE)  # Render level text
        screen.blit(score_text, (20, 20))  # Draw score text at position (20, 20)
        screen.blit(lives_text, (20, 50))  # Draw lives text at position (20, 50)
        screen.blit(level_text, (20, 80))  # Draw level text at position (20, 80)

        instr_rect = pygame.Rect(SCREEN_WIDTH - 210, 10, 200, 120)  # Create rectangle for instruction panel
        pygame.draw.rect(screen, UI_BG_COLOR, instr_rect)  # Draw semi-transparent instruction background
        for i, text in enumerate(instruction_texts):  # Iterate over instruction texts
            screen.blit(text, (SCREEN_WIDTH - 200, 20 + i * 20))  # Draw each instruction line with vertical spacing

        if game_over:  # Check if game is over
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # Create semi-transparent overlay surface
            draw_gradient(overlay, (50, 50, 50, 100), (100, 100, 100, 100))  # Draw gray gradient on overlay
            screen.blit(overlay, (0, 0))  # Draw overlay on screen
            result_text = "Game Over! Press R to Restart"  # Set game over message
            text = font.render(result_text, True, WHITE)  # Render game over text in white
            shadow = font.render(result_text, True, BLACK)  # Render shadow text in black
            screen.blit(shadow, (SCREEN_WIDTH // 2 - text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 2))  # Draw shadow slightly offset
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))  # Draw game over text centered
        elif win:  # Check if game is won
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # Create semi-transparent overlay surface
            draw_gradient(overlay, (50, 50, 150, 100), (100, 100, 200, 100))  # Draw blue-tinted gradient on overlay
            screen.blit(overlay, (0, 0))  # Draw overlay on screen
            congrats_text = "Congratulations! You've Conquered the Battlefield!"  # Set final congratulation message
            score_text = f"Final Score: {player.score}"  # Set final score message
            lives_text = f"Lives Remaining: {player.lives}"  # Set lives remaining message
            restart_text = "Press R to Restart"  # Set restart prompt
            text1 = congrats_font.render(congrats_text, True, WHITE)  # Render congratulation text in white (larger font)
            text2 = font.render(score_text, True, WHITE)  # Render score text in white
            text3 = font.render(lives_text, True, WHITE)  # Render lives text in white
            text4 = font.render(restart_text, True, WHITE)  # Render restart text in white
            shadow1 = congrats_font.render(congrats_text, True, BLACK)  # Render congratulation shadow in black
            shadow2 = font.render(score_text, True, BLACK)  # Render score shadow in black
            shadow3 = font.render(lives_text, True, BLACK)  # Render lives shadow in black
            shadow4 = font.render(restart_text, True, BLACK)  # Render restart shadow in black
            y_offset = SCREEN_HEIGHT // 2 - 80  # Calculate starting y position for centered text
            screen.blit(shadow1, (SCREEN_WIDTH // 2 - text1.get_width() // 2 + 2, y_offset + 2))  # Draw congratulation shadow
            screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, y_offset))  # Draw congratulation text
            screen.blit(shadow2, (SCREEN_WIDTH // 2 - text2.get_width() // 2 + 2, y_offset + 40 + 2))  # Draw score shadow
            screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, y_offset + 40))  # Draw score text
            screen.blit(shadow3, (SCREEN_WIDTH // 2 - text3.get_width() // 2 + 2, y_offset + 80 + 2))  # Draw lives shadow
            screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, y_offset + 80))  # Draw lives text
            screen.blit(shadow4, (SCREEN_WIDTH // 2 - text4.get_width() // 2 + 2, y_offset + 120 + 2))  # Draw restart shadow
            screen.blit(text4, (SCREEN_WIDTH // 2 - text4.get_width() // 2, y_offset + 120))  # Draw restart text
        elif level_complete:  # Check if level is complete
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # Create semi-transparent overlay surface
            draw_gradient(overlay, (50, 150, 50, 100), (100, 200, 100, 100))  # Draw green-tinted gradient for level complete
            screen.blit(overlay, (0, 0))  # Draw overlay on screen
            level_text = f"Level {current_level + 1} Complete! Advancing..."  # Set level complete message
            text = font.render(level_text, True, WHITE)  # Render level complete text in white
            shadow = font.render(level_text, True, BLACK)  # Render shadow text in black
            screen.blit(shadow, (SCREEN_WIDTH // 2 - text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 2))  # Draw shadow slightly offset
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))  # Draw level complete text centered

        pygame.display.flip()  # Update the screen with all drawn elements
        clock.tick(60)  # Limit frame rate to 60 FPS

if __name__ == "__main__":  # Check if script is run directly
    main()  # Call the main game function
