"""
Menu system for Sea Ping Warfare.
"""
import pygame
from config.settings import WIDTH, HEIGHT, UI_TEXT_COLOR


class MenuState:
    """Enum for menu states."""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    LEVEL_COMPLETE = "level_complete"


class Menu:
    def __init__(self):
        self.state = MenuState.MAIN_MENU
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_medium = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 32)
        self.font_tiny = pygame.font.SysFont(None, 24)
        
        # Colors
        self.title_color = (255, 255, 0)  # Yellow
        self.button_color = (100, 100, 100)
        self.button_hover_color = (150, 150, 150)
        self.text_color = UI_TEXT_COLOR
        self.background_color = (30, 60, 90, 200)  # Semi-transparent
        
        # Button dimensions
        self.button_width = 300
        self.button_height = 60
        self.button_margin = 20
        
        # Scrolling state for instructions
        self.scroll_offset = 0
        self.scroll_speed = 20

    def handle_events(self, events):
        """Handle menu events and return action."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == MenuState.PLAYING:
                        self.state = MenuState.PAUSED
                    elif self.state == MenuState.PAUSED:
                        self.state = MenuState.PLAYING
                    return "toggle_pause"
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.state == MenuState.MAIN_MENU:
                        action = self.handle_main_menu_click(mouse_pos)
                        if action:
                            return action
                    elif self.state == MenuState.PAUSED:
                        action = self.handle_pause_menu_click(mouse_pos)
                        if action:
                            return action
                    elif self.state == MenuState.LEVEL_COMPLETE:
                        action = self.handle_level_complete_click(mouse_pos)
                        if action:
                            return action
        
        return None

    def handle_main_menu_click(self, mouse_pos):
        """Handle clicks in main menu."""
        center_x = WIDTH // 2
        start_y = HEIGHT // 2 - 50
        
        # Start Game button
        start_rect = pygame.Rect(center_x - self.button_width // 2, start_y, 
                               self.button_width, self.button_height)
        if start_rect.collidepoint(mouse_pos):
            self.state = MenuState.PLAYING
            return "start_game"
            
        # Instructions button
        instructions_y = start_y + self.button_height + self.button_margin
        instructions_rect = pygame.Rect(center_x - self.button_width // 2, instructions_y,
                                      self.button_width, self.button_height)
        if instructions_rect.collidepoint(mouse_pos):
            return "show_instructions"
            
        # Quit button
        quit_y = instructions_y + self.button_height + self.button_margin
        quit_rect = pygame.Rect(center_x - self.button_width // 2, quit_y,
                              self.button_width, self.button_height)
        if quit_rect.collidepoint(mouse_pos):
            return "quit_game"
        
        return None

    def handle_pause_menu_click(self, mouse_pos):
        """Handle clicks in pause menu."""
        center_x = WIDTH // 2
        resume_y = HEIGHT // 2 - 80
        
        # Resume button
        resume_rect = pygame.Rect(center_x - self.button_width // 2, resume_y,
                                self.button_width, self.button_height)
        if resume_rect.collidepoint(mouse_pos):
            self.state = MenuState.PLAYING
            return "resume_game"
            
        # Instructions button
        instructions_y = resume_y + self.button_height + self.button_margin
        instructions_rect = pygame.Rect(center_x - self.button_width // 2, instructions_y,
                                      self.button_width, self.button_height)
        if instructions_rect.collidepoint(mouse_pos):
            return "show_instructions"
            
        # Main Menu button
        menu_y = instructions_y + self.button_height + self.button_margin
        menu_rect = pygame.Rect(center_x - self.button_width // 2, menu_y,
                              self.button_width, self.button_height)
        if menu_rect.collidepoint(mouse_pos):
            self.state = MenuState.MAIN_MENU
            return "main_menu"
        
        return None

    def handle_level_complete_click(self, mouse_pos):
        """Handle clicks in level complete screen."""
        center_x = WIDTH // 2
        continue_y = HEIGHT // 2 + 50
        
        # Continue button
        continue_rect = pygame.Rect(center_x - self.button_width // 2, continue_y,
                                  self.button_width, self.button_height)
        if continue_rect.collidepoint(mouse_pos):
            self.state = MenuState.PLAYING
            return "continue_level"
        
        return None

    def draw(self, surf):
        """Draw the current menu state."""
        if self.state == MenuState.MAIN_MENU:
            self.draw_main_menu(surf)
        elif self.state == MenuState.PAUSED:
            self.draw_pause_menu(surf)
        elif self.state == MenuState.LEVEL_COMPLETE:
            self.draw_level_complete(surf)

    def draw_main_menu(self, surf):
        """Draw the main menu."""
        # Semi-transparent background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 60, 90))
        surf.blit(overlay, (0, 0))
        
        center_x = WIDTH // 2
        
        # Title
        title = self.font_large.render("Sea-Ping Warfare", True, self.title_color)
        title_rect = title.get_rect(center=(center_x, HEIGHT // 4))
        surf.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Naval Combat Game", True, self.text_color)
        subtitle_rect = subtitle.get_rect(center=(center_x, HEIGHT // 4 + 60))
        surf.blit(subtitle, subtitle_rect)
        
        # Buttons
        start_y = HEIGHT // 2 - 50
        self.draw_button(surf, "Start Game", center_x, start_y)
        
        instructions_y = start_y + self.button_height + self.button_margin
        self.draw_button(surf, "Instructions", center_x, instructions_y)
        
        quit_y = instructions_y + self.button_height + self.button_margin
        self.draw_button(surf, "Quit Game", center_x, quit_y)

    def draw_pause_menu(self, surf):
        """Draw the pause menu overlay."""
        # Semi-transparent background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 60, 90))
        surf.blit(overlay, (0, 0))
        
        center_x = WIDTH // 2
        
        # Pause title
        title = self.font_large.render("PAUSED", True, self.title_color)
        title_rect = title.get_rect(center=(center_x, HEIGHT // 3))
        surf.blit(title, title_rect)
        
        # Buttons
        resume_y = HEIGHT // 2 - 80
        self.draw_button(surf, "Resume Game", center_x, resume_y)
        
        instructions_y = resume_y + self.button_height + self.button_margin
        self.draw_button(surf, "Instructions", center_x, instructions_y)
        
        menu_y = instructions_y + self.button_height + self.button_margin
        self.draw_button(surf, "Main Menu", center_x, menu_y)

    def draw_level_complete(self, surf):
        """Draw the level complete screen."""
        # Semi-transparent background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 60, 90))
        surf.blit(overlay, (0, 0))
        
        center_x = WIDTH // 2
        
        # Level complete title
        title = self.font_large.render("Level Complete!", True, self.title_color)
        title_rect = title.get_rect(center=(center_x, HEIGHT // 3))
        surf.blit(title, title_rect)
        
        # Continue button
        continue_y = HEIGHT // 2 + 50
        self.draw_button(surf, "Continue to Next Level", center_x, continue_y)

    def draw_button(self, surf, text, center_x, y):
        """Draw a button with hover effect."""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(center_x - self.button_width // 2, y, 
                                self.button_width, self.button_height)
        
        # Check if mouse is hovering
        color = self.button_hover_color if button_rect.collidepoint(mouse_pos) else self.button_color
        
        # Draw button background
        pygame.draw.rect(surf, color, button_rect)
        pygame.draw.rect(surf, self.text_color, button_rect, 3)
        
        # Draw button text
        text_surface = self.font_medium.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surf.blit(text_surface, text_rect)

    def draw_instructions(self, surf):
        """Draw a polished and professional instructions page that's universal for all screen sizes."""
        # Clean, dark background
        surf.fill((15, 25, 40))
        
        # Get screen dimensions for universal sizing
        screen_width, screen_height = surf.get_size()
        center_x = screen_width // 2
        
        # Handle scrolling input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.scroll_offset += self.scroll_speed
        
        # Calculate responsive font sizes and spacing
        title_size = max(48, screen_width // 20)  # Responsive title size
        subtitle_size = max(32, screen_width // 25)  # Responsive subtitle size
        header_size = max(28, screen_width // 30)  # Responsive header size
        body_size = max(20, screen_width // 40)  # Responsive body size
        
        # Create responsive fonts
        title_font = pygame.font.SysFont(None, title_size)
        subtitle_font = pygame.font.SysFont(None, subtitle_size)
        header_font = pygame.font.SysFont(None, header_size)
        body_font = pygame.font.SysFont(None, body_size)
        
        # Calculate responsive spacing
        margin = screen_width // 20  # Responsive margins
        section_spacing = screen_height // 8  # Responsive section spacing
        item_spacing = screen_height // 15  # Responsive item spacing
        
        # Start position with responsive top margin and scroll offset
        start_y = screen_height // 8 - self.scroll_offset
        
        # Title
        title = title_font.render("How to Play", True, (255, 215, 0))
        title_rect = title.get_rect(center=(center_x, start_y))
        surf.blit(title, title_rect)
        
        # Subtitle
        subtitle = subtitle_font.render("Master the art of naval warfare", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(center_x, start_y + title_size))
        surf.blit(subtitle, subtitle_rect)
        
        # Content area with responsive positioning and scroll offset
        content_start_y = start_y + title_size + subtitle_size + section_spacing
        
        # Section 1: Objective
        self._draw_section_header_responsive(surf, "Objective", center_x, content_start_y, header_font, margin)
        objective_text = "Destroy all enemy ships using strategic ricochet shots while avoiding their cannon fire."
        self._draw_section_content_responsive(surf, objective_text, center_x, content_start_y + header_size + item_spacing, 
                                            body_font, screen_width - margin * 2)
        
        # Section 2: Controls
        controls_y = content_start_y + section_spacing * 2
        self._draw_section_header_responsive(surf, "Controls", center_x, controls_y, header_font, margin)
        
        controls_data = [
            ("Movement", "WASD - Move your ship"),
            ("Aiming", "Arrow Keys - Aim your turret"),
            ("Firing", "Spacebar - Fire cannonball"),
            ("Pause", "ESC - Pause game / Open menu")
        ]
        
        control_item_y = controls_y + header_size + item_spacing
        for control_title, control_desc in controls_data:
            self._draw_control_item_responsive(surf, control_title, control_desc, center_x, control_item_y, body_font, margin)
            # More spacing for vertical layout (title + description + gap)
            control_item_y += item_spacing * 2.5
        
        # Section 3: Strategy
        strategy_y = control_item_y + item_spacing
        self._draw_section_header_responsive(surf, "Strategy", center_x, strategy_y, header_font, margin)
        
        strategy_items = [
            "Use obstacles and walls to bounce shots around corners",
            "You have 3 health points - enemies die in 1 hit",
            "Complete levels to progress and earn bonus points",
            "Stay mobile to avoid enemy fire",
            "Plan your ricochet angles carefully",
            "Watch enemy turret rotation patterns"
        ]
        
        strategy_item_y = strategy_y + header_size + item_spacing
        for strategy_item in strategy_items:
            self._draw_strategy_item_responsive(surf, strategy_item, center_x, strategy_item_y, body_font, margin)
            strategy_item_y += item_spacing
        
        # Calculate total content height to determine if scrolling is needed
        total_content_height = strategy_item_y - start_y + 100  # Add some padding
        
        # Visual separator (fixed at bottom)
        separator_y = screen_height - screen_height // 6
        self._draw_separator_responsive(surf, center_x, separator_y, screen_width)
        
        # Scroll instructions (show if content is taller than screen)
        if total_content_height > screen_height - 200:
            scroll_text = body_font.render("Use UP/DOWN or W/S to scroll", True, (150, 150, 150))
            scroll_rect = scroll_text.get_rect(center=(center_x, screen_height - 40))
            surf.blit(scroll_text, scroll_rect)
        
        # Back button with responsive sizing (fixed at bottom)
        back_y = screen_height - screen_height // 12
        self._draw_back_button_responsive(surf, center_x, back_y, screen_width, screen_height)

    def _draw_section_header_responsive(self, surf, text, center_x, y, font, margin):
        """Draw a section header with responsive sizing."""
        text_surface = font.render(text, True, (255, 215, 0))
        text_rect = text_surface.get_rect(center=(center_x, y))
        
        # Responsive padding
        padding = margin // 3
        bg_rect = pygame.Rect(text_rect.left - padding, text_rect.top - padding // 2, 
                             text_rect.width + padding * 2, text_rect.height + padding)
        pygame.draw.rect(surf, (30, 45, 60), bg_rect, border_radius=padding // 2)
        pygame.draw.rect(surf, (255, 215, 0), bg_rect, 2, border_radius=padding // 2)
        
        surf.blit(text_surface, text_rect)

    def _draw_section_content_responsive(self, surf, text, center_x, y, font, max_width):
        """Draw section content with responsive word wrapping."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_surface = font.render(test_line, True, (220, 220, 220))
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw each line with responsive spacing
        line_height = font.get_height() + 4
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, (220, 220, 220))
            line_rect = line_surface.get_rect(center=(center_x, y + i * line_height))
            surf.blit(line_surface, line_rect)

    def _draw_control_item_responsive(self, surf, title, description, center_x, y, font, margin):
        """Draw a control item with clean vertical stack layout."""
        # Title (centered)
        title_surface = font.render(title, True, (255, 215, 0))
        title_rect = title_surface.get_rect(center=(center_x, y))
        surf.blit(title_surface, title_rect)
        
        # Description (centered below title)
        desc_surface = font.render(description, True, (200, 200, 200))
        desc_rect = desc_surface.get_rect(center=(center_x, y + font.get_height() + 8))
        surf.blit(desc_surface, desc_rect)

    def _draw_strategy_item_responsive(self, surf, text, center_x, y, font, margin):
        """Draw a strategy item with responsive bullet point."""
        # Bullet point
        bullet_surface = font.render("•", True, (255, 215, 0))
        bullet_x = center_x - margin
        surf.blit(bullet_surface, (bullet_x, y))
        
        # Strategy text
        text_surface = font.render(text, True, (200, 200, 200))
        text_x = bullet_x + font.get_height() // 2
        surf.blit(text_surface, (text_x, y))

    def _draw_separator_responsive(self, surf, center_x, y, screen_width):
        """Draw a responsive separator line."""
        line_width = screen_width // 3
        pygame.draw.line(surf, (100, 100, 100), (center_x - line_width, y), (center_x + line_width, y), 2)
        
        # Responsive decorative elements
        dot_count = 3
        for i in range(dot_count):
            x_offset = center_x - line_width // 2 + (i * line_width // (dot_count - 1))
            pygame.draw.circle(surf, (255, 215, 0), (x_offset, y), 4)

    def _draw_back_button_responsive(self, surf, center_x, y, screen_width, screen_height):
        """Draw a responsive back button."""
        # Responsive button size
        button_width = min(screen_width // 3, 300)
        button_height = min(screen_height // 12, 60)
        button_rect = pygame.Rect(center_x - button_width // 2, y, button_width, button_height)
        
        # Check for hover
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)
        
        # Responsive border radius
        border_radius = min(button_height // 5, 10)
        
        # Button background
        bg_color = (70, 90, 110) if is_hovered else (50, 70, 90)
        pygame.draw.rect(surf, bg_color, button_rect, border_radius=border_radius)
        
        # Border
        border_color = (255, 215, 0) if is_hovered else (120, 120, 120)
        border_width = max(2, button_height // 20)
        pygame.draw.rect(surf, border_color, button_rect, border_width, border_radius=border_radius)
        
        # Responsive button text
        text = "Back to Menu"
        text_size = max(20, button_height // 3)
        text_font = pygame.font.SysFont(None, text_size)
        text_color = (255, 255, 255) if is_hovered else (230, 230, 230)
        text_surface = text_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surf.blit(text_surface, text_rect)

    def set_state(self, state):
        """Set the menu state."""
        self.state = state

    def is_menu_active(self):
        """Check if any menu is currently active."""
        return self.state != MenuState.PLAYING

    def is_back_button_clicked(self, mouse_pos):
        """Check if the back button in instructions screen was clicked."""
        # Get screen dimensions for responsive button detection
        screen_width, screen_height = pygame.display.get_surface().get_size()
        center_x = screen_width // 2
        
        # Responsive button size (same as in draw function)
        button_width = min(screen_width // 3, 300)
        button_height = min(screen_height // 12, 60)
        back_y = screen_height - screen_height // 12
        
        back_rect = pygame.Rect(center_x - button_width // 2, back_y, button_width, button_height)
        return back_rect.collidepoint(mouse_pos)

    def reset_scroll(self):
        """Reset scroll offset when entering instructions."""
        self.scroll_offset = 0 