"""
Main entry point for Sea Ping Warfare.
"""
import pygame
import sys
from config.settings import WIDTH, HEIGHT, FPS, OBSTACLE_COLOR, MAX_HEALTH
from game.entities import Player, Enemy, Cannonball
from game.levels import get_level_data
from game.ui import HUD, Menu, MenuState
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
    menu = Menu()
    current_level = 1
    enemies, obstacles = get_level_data(current_level)
    cannonballs = []
    game_over = False
    restart = False
    score = 0
    level_complete = False
    showing_instructions = False

    while True:
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                restart = True
                
        if restart:
            main()
            return

        # Handle menu events
        menu_action = menu.handle_events(events)
        if menu_action:
            if menu_action == "start_game":
                menu.set_state(MenuState.PLAYING)
            elif menu_action == "resume_game":
                menu.set_state(MenuState.PLAYING)
            elif menu_action == "main_menu":
                # Reset game state
                player = Player()
                current_level = 1
                enemies, obstacles = get_level_data(current_level)
                cannonballs = []
                game_over = False
                score = 0
                level_complete = False
            elif menu_action == "quit_game":
                pygame.quit()
                sys.exit()
            elif menu_action == "show_instructions":
                showing_instructions = True
                menu.reset_scroll()  # Reset scroll when entering instructions
            elif menu_action == "continue_level":
                # Progress to next level
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
                level_complete = False
                menu.set_state(MenuState.PLAYING)

        # --- Update ---
        if not game_over and menu.state == MenuState.PLAYING and not level_complete:
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
            
            # Check for level completion
            alive_enemies = [e for e in enemies if e.alive and not e.is_dying]
            if len(alive_enemies) == 0 and len(enemies) > 0:
                # All enemies are dead or dying, show level complete
                level_complete = True
                menu.set_state(MenuState.LEVEL_COMPLETE)
            
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
        
        # Draw HUD (only score and level when playing)
        if menu.state == MenuState.PLAYING:
            hud.draw_score(screen, score)
            hud.draw_level(screen, current_level)
        
        # Draw instructions page (full screen)
        if showing_instructions:
            menu.draw_instructions(screen)
            # Check for back button click
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:  # Left click
                if menu.is_back_button_clicked(mouse_pos):
                    showing_instructions = False
        # Draw menu (only if not showing instructions)
        elif menu.is_menu_active():
            menu.draw(screen)
        
        # Draw game over screen
        if game_over:
            hud.draw_game_over(screen, current_level)
        
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main() 