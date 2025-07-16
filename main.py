"""
Main entry point for Sea Ping Warfare.
"""
import pygame
import sys
from config.settings import WIDTH, HEIGHT, FPS, OBSTACLE_COLOR, MAX_HEALTH
from game.entities import Player, Enemy, Cannonball
from game.levels import get_level_data
from game.ui import HUD
from game.physics import check_cannonball_collisions


def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sea-Ping Warfare (Pygame)")
    clock = pygame.time.Clock()
    
    # Initialize game objects
    player = Player()
    hud = HUD()
    current_level = 1
    enemies, obstacles = get_level_data(current_level)
    cannonballs = []
    game_over = False
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                restart = True
                
        if restart:
            main()
            return

        # --- Update ---
        if not game_over:
            # Player update
            cb = player.update(keys, mouse_pos, mouse_buttons, obstacles, cannonballs)
            if cb:
                cannonballs.append(cb)
                
            # Enemy updates
            for enemy in enemies:
                cb = enemy.update(player, obstacles, cannonballs)
                if cb:
                    cannonballs.append(cb)
                    
            # Cannonball updates
            for cb in cannonballs:
                cb.update(obstacles)
            cannonballs = [cb for cb in cannonballs if cb.alive]

            # Collision detection
            score += check_cannonball_collisions(cannonballs, player, enemies)
            
            # Remove dead enemies and check level completion
            enemies = [e for e in enemies if e.alive]
            if len(enemies) == 0:
                # Level completed - progress to next level
                current_level += 1
                enemies, obstacles = get_level_data(current_level)
                # Reset player position and health for new level
                player.x, player.y = WIDTH // 2, HEIGHT - 80
                player.health = MAX_HEALTH
                player.hit_flash_timer = 0
                # Clear all cannonballs for clean start
                cannonballs = []
                # Add some score bonus for completing level
                score += current_level * 10
            
            # Check game over
            if not player.alive:
                game_over = True

        # --- Draw ---
        screen.fill((30, 60, 90))
        
        # Draw obstacles
        for rect in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, rect)
            
        # Draw game objects
        for cb in cannonballs:
            cb.draw(screen)
        if player.alive:
            player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw HUD
        hud.draw_all(screen, score, current_level, player.health, MAX_HEALTH)
        
        # Draw game over screen
        if game_over:
            hud.draw_game_over(screen, current_level)
        
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main() 