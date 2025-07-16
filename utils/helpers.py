"""
Utility functions for Sea Ping Warfare.
"""
import math
import pygame


def angle_to(vec):
    """Convert vector to angle."""
    return math.atan2(vec[1], vec[0])


def clamp(val, minv, maxv):
    """Clamp value between min and max."""
    return max(minv, min(val, maxv))


def vec_from_angle(angle, length):
    """Create vector from angle and length."""
    return (math.cos(angle) * length, math.sin(angle) * length)


def dist(a, b):
    """Calculate distance between two points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def reflect_velocity(vx, vy, normal_x, normal_y):
    """Calculate reflection of velocity vector off a surface normal."""
    dot_product = vx * normal_x + vy * normal_y
    reflected_x = vx - 2 * dot_product * normal_x
    reflected_y = vy - 2 * dot_product * normal_y
    return reflected_x, reflected_y


def make_obstacles():
    """Create default obstacle layout."""
    return [
        pygame.Rect(200, 150, 80, 200),
        pygame.Rect(500, 100, 60, 300),
        pygame.Rect(350, 400, 120, 40),
        pygame.Rect(100, 500, 200, 40),
        pygame.Rect(600, 500, 80, 40),
    ] 