"""
Collision detection for Sea Ping Warfare.
"""
from utils.helpers import dist
from config.settings import PLAYER_RADIUS, ENEMY_RADIUS, CANNONBALL_RADIUS


def check_cannonball_collisions(cannonballs, player, enemies):
    """Check collisions between cannonballs and ships."""
    score = 0
    
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
                break
    
    return score 