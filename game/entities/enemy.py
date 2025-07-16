"""
Enemy entity for Sea Ping Warfare.
"""
import math
import pygame
import random
from config.settings import (
    ENEMY_RADIUS, TURRET_LENGTH, ENEMY_FIRE_INTERVAL, MAX_CANNONBALLS,
    MAX_HEALTH, HIT_FLASH_DURATION, ENEMY_COLOR, ENEMY_TURRET_COLOR,
    ENEMY_AIM_SPEED
)
from game.entities.cannonball import Cannonball


class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.turret_angle = 0
        self.cooldown = random.randint(0, ENEMY_FIRE_INTERVAL)
        self.alive = True
        self.health = MAX_HEALTH
        self.hit_flash_timer = 0
        self.death_timer = 0
        self.is_dying = False

    def update(self, player, obstacles, cannonballs):
        if not self.alive:
            return None
            
        # Update death animation
        if self.is_dying:
            self.death_timer += 1
            if self.death_timer > 60:  # 1 second at 60 FPS
                self.alive = False
            return None
            
        # Update hit flash timer
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            
        # Smooth AI: rotate turret toward player with slower speed
        target_angle = math.atan2(player.y - self.y, player.x - self.x)
        # Smooth rotation towards target angle
        angle_diff = target_angle - self.turret_angle
        # Normalize angle difference to [-π, π]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        self.turret_angle += angle_diff * ENEMY_AIM_SPEED
        
        # Firing (limit active cannonballs)
        if self.cooldown > 0:
            self.cooldown -= 1
        active_cannonballs = sum(1 for cb in cannonballs if cb.owner == 'enemy' and cb.alive)
        if self.cooldown == 0 and self.alive and player.alive and active_cannonballs < MAX_CANNONBALLS:
            self.cooldown = ENEMY_FIRE_INTERVAL
            return Cannonball((self.x + math.cos(self.turret_angle)*TURRET_LENGTH, self.y + math.sin(self.turret_angle)*TURRET_LENGTH), self.turret_angle, 'enemy')
        return None

    def draw(self, surf):
        if self.is_dying:
            # Death animation - flashing and shrinking
            flash_intensity = (self.death_timer // 3) % 2
            if flash_intensity:
                ship_color = (255, 255, 255)  # White flash
            else:
                ship_color = (255, 0, 0)  # Red flash
                
            # Shrink the enemy as it dies
            shrink_factor = 1.0 - (self.death_timer / 60.0)
            radius = int(ENEMY_RADIUS * shrink_factor)
            if radius > 0:
                pygame.draw.circle(surf, ship_color, (int(self.x), int(self.y)), radius)
                # Draw shrinking turret
                tx = self.x + math.cos(self.turret_angle) * (TURRET_LENGTH * shrink_factor)
                ty = self.y + math.sin(self.turret_angle) * (TURRET_LENGTH * shrink_factor)
                pygame.draw.line(surf, ENEMY_TURRET_COLOR, (self.x, self.y), (tx, ty), int(8 * shrink_factor))
        else:
            # Normal drawing
            # Determine ship color based on hit flash
            if self.hit_flash_timer > 0 and self.hit_flash_timer % 6 < 3:
                ship_color = (255, 255, 255)  # White flash when hit
            else:
                ship_color = ENEMY_COLOR
                
            pygame.draw.circle(surf, ship_color, (int(self.x), int(self.y)), ENEMY_RADIUS)
            tx = self.x + math.cos(self.turret_angle) * TURRET_LENGTH
            ty = self.y + math.sin(self.turret_angle) * TURRET_LENGTH
            pygame.draw.line(surf, ENEMY_TURRET_COLOR, (self.x, self.y), (tx, ty), 8)

    def hit(self):
        # Start death animation
        self.is_dying = True
        self.death_timer = 0

    def pos(self):
        return (self.x, self.y) 