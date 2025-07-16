"""
Enemy entity for Sea Ping Warfare.
"""
import math
import pygame
import random
from config.settings import (
    ENEMY_RADIUS, TURRET_LENGTH, ENEMY_FIRE_INTERVAL, MAX_CANNONBALLS,
    MAX_HEALTH, HIT_FLASH_DURATION, ENEMY_COLOR, ENEMY_TURRET_COLOR
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

    def update(self, player, obstacles, cannonballs):
        if not self.alive:
            return None
            
        # Update hit flash timer
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            
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
        # Reduce health instead of instant death
        self.health -= 1
        self.hit_flash_timer = HIT_FLASH_DURATION
        if self.health <= 0:
            self.alive = False

    def pos(self):
        return (self.x, self.y) 