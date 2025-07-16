"""
HUD (Heads Up Display) for Sea Ping Warfare.
"""
import pygame
from config.settings import UI_TEXT_COLOR, WIDTH, HEIGHT


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)

    def draw_score(self, surf, score):
        """Draw score display."""
        score_text = self.font.render(f"Score: {score}", True, UI_TEXT_COLOR)
        surf.blit(score_text, (10, 10))

    def draw_level(self, surf, level):
        """Draw level display."""
        level_text = self.font.render(f"Level: {level}", True, UI_TEXT_COLOR)
        surf.blit(level_text, (10, 30))

    def draw_health(self, surf, health, max_health):
        """Draw player health display."""
        health_text = self.font.render(f"Health: {health}/{max_health}", True, UI_TEXT_COLOR)
        surf.blit(health_text, (10, 50))

    def draw_controls(self, surf):
        """Draw controls display."""
        controls_text = self.small_font.render("WASD: Move | Arrows: Aim | Space: Fire", True, UI_TEXT_COLOR)
        surf.blit(controls_text, (WIDTH - controls_text.get_width() - 10, 10))

    def draw_game_over(self, surf, level):
        """Draw game over screen."""
        txt = self.font.render("Game Over! Press R to Restart", True, UI_TEXT_COLOR)
        surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 40))
        level_txt = self.font.render(f"You reached Level {level}", True, UI_TEXT_COLOR)
        surf.blit(level_txt, (WIDTH//2 - level_txt.get_width()//2, HEIGHT//2 + 10))

    def draw_all(self, surf, score, level, health, max_health):
        """Draw all HUD elements."""
        self.draw_score(surf, score)
        self.draw_level(surf, level)
        self.draw_health(surf, health, max_health)
        self.draw_controls(surf) 