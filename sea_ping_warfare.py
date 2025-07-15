import pygame
import sys
import math
import random

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 3.0
PLAYER_RADIUS = 22
TURRET_LENGTH = 28
CANNONBALL_RADIUS = 7
CANNONBALL_SPEED = 8.0  # Increased speed
CANNONBALL_BOUNCES = 2  # Reduced to 2 bounces
ENEMY_RADIUS = 22
ENEMY_SPEED = 1.5
ENEMY_FIRE_INTERVAL = 180  # Increased from 120 to 180 (slower firing)
OBSTACLE_COLOR = (80, 80, 80)
MAX_CANNONBALLS = 2  # Limit active cannonballs

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sea-Ping Warfare (Pygame)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 24)

# --- Helper Functions ---
def angle_to(vec):
    return math.atan2(vec[1], vec[0])

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

def vec_from_angle(angle, length):
    return (math.cos(angle) * length, math.sin(angle) * length)

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def reflect_velocity(vx, vy, normal_x, normal_y):
    """Calculate reflection of velocity vector off a surface normal"""
    dot_product = vx * normal_x + vy * normal_y
    reflected_x = vx - 2 * dot_product * normal_x
    reflected_y = vy - 2 * dot_product * normal_y
    return reflected_x, reflected_y

# --- Classes ---
class Cannonball:
    def __init__(self, pos, angle, owner):
        self.x, self.y = pos
        self.angle = angle
        self.vx = math.cos(angle) * CANNONBALL_SPEED
        self.vy = math.sin(angle) * CANNONBALL_SPEED
        self.bounces = 0
        self.owner = owner  # 'player' or 'enemy'
        self.alive = True
        self.lifetime = 300  # Increased lifetime
        self.color = (30, 144, 255) if owner == 'player' else (255, 100, 40)

    def update(self, obstacles):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        # Bounce off walls with proper reflection
        if self.x - CANNONBALL_RADIUS < 0:
            self.x = CANNONBALL_RADIUS
            self.vx = abs(self.vx)  # Reflect right
            self.bounces += 1
        elif self.x + CANNONBALL_RADIUS > WIDTH:
            self.x = WIDTH - CANNONBALL_RADIUS
            self.vx = -abs(self.vx)  # Reflect left
            self.bounces += 1
            
        if self.y - CANNONBALL_RADIUS < 0:
            self.y = CANNONBALL_RADIUS
            self.vy = abs(self.vy)  # Reflect down
            self.bounces += 1
        elif self.y + CANNONBALL_RADIUS > HEIGHT:
            self.y = HEIGHT - CANNONBALL_RADIUS
            self.vy = -abs(self.vy)  # Reflect up
            self.bounces += 1
        
        # Bounce off obstacles with improved collision detection
        for rect in obstacles:
            # Check if cannonball is inside the rectangle
            if (rect.left <= self.x <= rect.right and rect.top <= self.y <= rect.bottom):
                # Determine which side of the rectangle was hit
                # Calculate distances to each edge
                dist_left = self.x - rect.left
                dist_right = rect.right - self.x
                dist_top = self.y - rect.top
                dist_bottom = rect.bottom - self.y
                
                # Find the closest edge
                min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
                
                if min_dist == dist_left:  # Hit left edge
                    self.x = rect.left - CANNONBALL_RADIUS
                    self.vx = -abs(self.vx)  # Reflect left
                elif min_dist == dist_right:  # Hit right edge
                    self.x = rect.right + CANNONBALL_RADIUS
                    self.vx = abs(self.vx)  # Reflect right
                elif min_dist == dist_top:  # Hit top edge
                    self.y = rect.top - CANNONBALL_RADIUS
                    self.vy = -abs(self.vy)  # Reflect up
                elif min_dist == dist_bottom:  # Hit bottom edge
                    self.y = rect.bottom + CANNONBALL_RADIUS
                    self.vy = abs(self.vy)  # Reflect down
                
                self.bounces += 1
                break
        
        # Destroy after 2 bounces or timeout
        if self.bounces > CANNONBALL_BOUNCES or self.lifetime <= 0:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), CANNONBALL_RADIUS)

    def pos(self):
        return (self.x, self.y)

class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT - 80
        self.angle = 0
        self.turret_angle = 0
        self.cooldown = 0
        self.alive = True
        self.aim_speed = 0.1  # Speed for arrow key aiming

    def update(self, keys, mouse_pos, mouse_buttons, obstacles, cannonballs):
        if not self.alive:
            return None
        # Movement with WASD
        dx = (keys[pygame.K_d]) - (keys[pygame.K_a])
        dy = (keys[pygame.K_s]) - (keys[pygame.K_w])
        move_vec = pygame.Vector2(dx, dy)
        if move_vec.length() > 0:
            move_vec = move_vec.normalize() * PLAYER_SPEED
            new_x = self.x + move_vec.x
            new_y = self.y + move_vec.y
            # Prevent moving into obstacles
            player_rect = pygame.Rect(new_x-PLAYER_RADIUS, new_y-PLAYER_RADIUS, PLAYER_RADIUS*2, PLAYER_RADIUS*2)
            if not any(player_rect.colliderect(rect) for rect in obstacles):
                # Clamp to screen bounds
                new_x = clamp(new_x, PLAYER_RADIUS, WIDTH - PLAYER_RADIUS)
                new_y = clamp(new_y, PLAYER_RADIUS, HEIGHT - PLAYER_RADIUS)
                self.x, self.y = new_x, new_y
        
        # Aiming with arrow keys
        aim_dx = (keys[pygame.K_RIGHT]) - (keys[pygame.K_LEFT])
        aim_dy = (keys[pygame.K_DOWN]) - (keys[pygame.K_UP])
        if aim_dx != 0 or aim_dy != 0:
            target_angle = math.atan2(aim_dy, aim_dx)
            # Smooth rotation towards target angle
            angle_diff = target_angle - self.turret_angle
            # Normalize angle difference to [-π, π]
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            self.turret_angle += angle_diff * self.aim_speed
        
        # Firing with spacebar
        if self.cooldown > 0:
            self.cooldown -= 1
        active_cannonballs = sum(1 for cb in cannonballs if cb.owner == 'player' and cb.alive)
        if keys[pygame.K_SPACE] and self.cooldown == 0 and active_cannonballs < MAX_CANNONBALLS:
            self.cooldown = 15  # Faster firing
            return Cannonball((self.x + math.cos(self.turret_angle)*TURRET_LENGTH, self.y + math.sin(self.turret_angle)*TURRET_LENGTH), self.turret_angle, 'player')
        return None

    def draw(self, surf):
        # Draw ship body
        pygame.draw.circle(surf, (0, 200, 255), (int(self.x), int(self.y)), PLAYER_RADIUS)
        # Draw turret (longer and bright cyan color)
        tx = self.x + math.cos(self.turret_angle) * (TURRET_LENGTH + 10)
        ty = self.y + math.sin(self.turret_angle) * (TURRET_LENGTH + 10)
        pygame.draw.line(surf, (0, 255, 255), (self.x, self.y), (tx, ty), 10)
        # Draw aiming reticle
        reticle_x = self.x + math.cos(self.turret_angle) * 120
        reticle_y = self.y + math.sin(self.turret_angle) * 120
        pygame.draw.circle(surf, (0, 255, 255), (int(reticle_x), int(reticle_y)), 6, 2)

    def hit(self):
        # One-hit kill
        self.alive = False

    def pos(self):
        return (self.x, self.y)

class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.turret_angle = 0
        self.cooldown = random.randint(0, ENEMY_FIRE_INTERVAL)
        self.alive = True

    def update(self, player, obstacles, cannonballs):
        if not self.alive:
            return None
        # Simple AI: rotate turret toward player
        self.turret_angle = math.atan2(player.y - self.y, player.x - self.x)
        # Firing (limit active cannonballs)
        if self.cooldown > 0:
            self.cooldown -= 1
        active_cannonballs = sum(1 for cb in cannonballs if cb.owner == 'enemy' and cb.alive)
        if self.cooldown == 0 and self.alive and player.alive and active_cannonballs < MAX_CANNONBALLS:
            self.cooldown = ENEMY_FIRE_INTERVAL
            return Cannonball((self.x + math.cos(self.turret_angle)*TURRET_LENGTH, self.y + math.sin(self.turret_angle)*TURRET_LENGTH), self.turret_angle, 'enemy')
        return None

    def draw(self, surf):
        pygame.draw.circle(surf, (255, 80, 80), (int(self.x), int(self.y)), ENEMY_RADIUS)
        tx = self.x + math.cos(self.turret_angle) * TURRET_LENGTH
        ty = self.y + math.sin(self.turret_angle) * TURRET_LENGTH
        pygame.draw.line(surf, (200, 0, 0), (self.x, self.y), (tx, ty), 8)

    def hit(self):
        # One-hit kill
        self.alive = False

    def pos(self):
        return (self.x, self.y)

# --- Obstacles ---
def make_obstacles():
    # List of pygame.Rects
    obstacles = [
        pygame.Rect(200, 150, 80, 200),
        pygame.Rect(500, 100, 60, 300),
        pygame.Rect(350, 400, 120, 40),
        pygame.Rect(100, 500, 200, 40),
        pygame.Rect(600, 500, 80, 40),
    ]
    return obstacles

# --- Game Loop ---
def main():
    player = Player()
    enemies = [Enemy(120, 120), Enemy(700, 120), Enemy(400, 300)]
    cannonballs = []
    obstacles = make_obstacles()
    game_over = False
    victory = False
    restart = False
    score = 0

    while True:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and (game_over or victory):
                restart = True
        if restart:
            main()
            return

        # --- Update ---
        if not (game_over or victory):
            cb = player.update(keys, mouse_pos, mouse_buttons, obstacles, cannonballs)
            if cb:
                cannonballs.append(cb)
            for enemy in enemies:
                cb = enemy.update(player, obstacles, cannonballs)
                if cb:
                    cannonballs.append(cb)
            for cb in cannonballs:
                cb.update(obstacles)
            cannonballs = [cb for cb in cannonballs if cb.alive]

            # --- Collisions (No friendly fire) ---
            for cb in cannonballs:
                if cb.owner == 'player':
                    # Player cannonballs only hit enemies
                    for enemy in enemies:
                        if enemy.alive and dist(cb.pos(), enemy.pos()) < ENEMY_RADIUS + CANNONBALL_RADIUS:
                            enemy.hit()
                            cb.alive = False
                            score += 1
                            break
                elif cb.owner == 'enemy':
                    # Enemy cannonballs only hit player
                    if player.alive and dist(cb.pos(), player.pos()) < PLAYER_RADIUS + CANNONBALL_RADIUS:
                        player.hit()
                        cb.alive = False
                        if not player.alive:
                            game_over = True
                            break
            
            enemies = [e for e in enemies if e.alive]
            if len(enemies) == 0:
                victory = True

        # --- Draw ---
        screen.fill((30, 60, 90))
        for rect in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, rect)
        for cb in cannonballs:
            cb.draw(screen)
        if player.alive:
            player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        
        # Score display
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # Controls display
        controls_text = small_font.render("WASD: Move | Arrows: Aim | Space: Fire", True, (255, 255, 255))
        screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, 10))
        
        # UI
        if game_over:
            txt = font.render("Game Over! Press R to Restart", True, (255, 255, 255))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 40))
        elif victory:
            txt = font.render("Victory! Press R to Restart", True, (255, 255, 0))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 40))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main() 