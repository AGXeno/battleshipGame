"""
Level data and configurations for Sea Ping Warfare.
"""
import pygame
import random
from config.settings import WIDTH, HEIGHT
from game.entities.enemy import Enemy


def get_level_data(level):
    """Return enemy positions and obstacles for a given level."""
    if level == 1:
        enemies = [Enemy(400, 200)]
        obstacles = make_level_1_obstacles()
    elif level == 2:
        enemies = [Enemy(400, 200)]
        obstacles = make_level_2_obstacles()
    elif level == 3:
        enemies = [Enemy(400, 200)]
        obstacles = make_level_3_obstacles()
    else:
        # For levels beyond 3, generate random enemies and obstacles
        enemies, obstacles = generate_random_level(level)
    
    return enemies, obstacles


def make_level_1_obstacles():
    """Create obstacles for level 1."""
    return [
        pygame.Rect(200, 150, 80, 200),
        pygame.Rect(500, 100, 60, 300),
        pygame.Rect(350, 400, 120, 40),
        pygame.Rect(100, 500, 200, 40),
        pygame.Rect(600, 500, 80, 40),
    ]


def make_level_2_obstacles():
    """Create obstacles for level 2."""
    return [
        pygame.Rect(150, 150, 100, 200),
        pygame.Rect(550, 100, 80, 250),
        pygame.Rect(300, 350, 150, 50),
        pygame.Rect(50, 450, 200, 40),
        pygame.Rect(650, 450, 100, 40),
    ]


def make_level_3_obstacles():
    """Create obstacles for level 3."""
    return [
        pygame.Rect(200, 100, 60, 300),
        pygame.Rect(540, 100, 60, 300),
        pygame.Rect(350, 300, 100, 60),
        pygame.Rect(100, 500, 150, 40),
        pygame.Rect(550, 500, 150, 40),
    ]


def generate_random_level(level):
    """Generate random enemies and obstacles for levels beyond 3."""
    enemies = []
    for _ in range(min(1 + level // 3, 3)):  # 1 enemy for most levels, max 3
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT // 2)
        enemies.append(Enemy(x, y))
    
    obstacles = []
    for _ in range(3 + level // 2):  # More obstacles in higher levels
        x = random.randint(50, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        w = random.randint(40, 120)
        h = random.randint(40, 200)
        obstacles.append(pygame.Rect(x, y, w, h))
    
    return enemies, obstacles 