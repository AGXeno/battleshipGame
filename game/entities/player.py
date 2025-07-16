"""
Player entity for Sea Ping Warfare.
"""
import math
import pygame
from config.settings import (
    PLAYER_SPEED, PLAYER_RADIUS, TURRET_LENGTH, PLAYER_AIM_SPEED,
    MAX_HEALTH, HIT_FLASH_DURATION, MAX_CANNONBALLS,
    PLAYER_COLOR, PLAYER_TURRET_COLOR, WIDTH, HEIGHT
)
from utils.helpers import clamp
from game.entities.cannonball import Cannonball


class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT - 80
        self.angle = 0
        self.turret_angle = 0
        self.cooldown = 0
        self.alive = True
        self.health = MAX_HEALTH
        self.hit_flash_timer = 0
        self.aim_speed = PLAYER_AIM_SPEED

    def update(self, keys, mouse_pos, mouse_buttons, obstacles, cannonballs):
        if not self.alive:
            return None
        
        # Update hit flash timer
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            
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
        # Determine ship color based on hit flash
        if self.hit_flash_timer > 0 and self.hit_flash_timer % 6 < 3:
            ship_color = (255, 255, 255)  # White flash when hit
        else:
            ship_color = PLAYER_COLOR
            
        # Draw ship body
        pygame.draw.circle(surf, ship_color, (int(self.x), int(self.y)), PLAYER_RADIUS)
        # Draw turret (longer and bright cyan color)
        tx = self.x + math.cos(self.turret_angle) * (TURRET_LENGTH + 10)
        ty = self.y + math.sin(self.turret_angle) * (TURRET_LENGTH + 10)
        pygame.draw.line(surf, PLAYER_TURRET_COLOR, (self.x, self.y), (tx, ty), 10)
        # Draw aiming reticle
        reticle_x = self.x + math.cos(self.turret_angle) * 120
        reticle_y = self.y + math.sin(self.turret_angle) * 120
        pygame.draw.circle(surf, PLAYER_TURRET_COLOR, (int(reticle_x), int(reticle_y)), 6, 2)
        
        # Draw health bar
        self.draw_health_bar(surf)

    def draw_health_bar(self, surf):
        # Health bar position (above the ship)
        bar_width = 60
        bar_height = 8
        bar_x = self.x - bar_width // 2
        bar_y = self.y - PLAYER_RADIUS - 20
        
        # Background (gray)
        pygame.draw.rect(surf, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
        
        # Health segments (3 segments)
        segment_width = bar_width // 3
        for i in range(self.health):
            segment_x = bar_x + i * segment_width
            pygame.draw.rect(surf, (0, 255, 0), (segment_x, bar_y, segment_width - 1, bar_height))
        
        # Border
        pygame.draw.rect(surf, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def hit(self):
        # Reduce health instead of instant death
        self.health -= 1
        self.hit_flash_timer = HIT_FLASH_DURATION
        if self.health <= 0:
            self.alive = False

    def pos(self):
        return (self.x, self.y) 