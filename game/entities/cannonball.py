"""
Cannonball entity for Sea Ping Warfare.
"""
import math
import pygame
from config.settings import (
    CANNONBALL_RADIUS, CANNONBALL_SPEED, CANNONBALL_BOUNCES,
    PLAYER_CANNONBALL_COLOR, ENEMY_CANNONBALL_COLOR,
    WIDTH, HEIGHT
)


class Cannonball:
    def __init__(self, pos, angle, owner):
        self.x, self.y = pos
        self.angle = angle
        self.vx = math.cos(angle) * CANNONBALL_SPEED
        self.vy = math.sin(angle) * CANNONBALL_SPEED
        self.bounces = 0
        self.owner = owner  # 'player' or 'enemy'
        self.alive = True
        self.lifetime = 300
        self.color = PLAYER_CANNONBALL_COLOR if owner == 'player' else ENEMY_CANNONBALL_COLOR

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
        
        # Destroy after max bounces or timeout
        if self.bounces > CANNONBALL_BOUNCES or self.lifetime <= 0:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), CANNONBALL_RADIUS)

    def pos(self):
        return (self.x, self.y) 