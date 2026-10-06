import math
import pygame


class Rope:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_y = screen_height // 2
        self.marker_x = screen_width // 2

        self.left_win_x = 180
        self.right_win_x = screen_width - 180
        self.pull_step = 12

    def pull_left(self, strength=1.0):
        self.marker_x -= int(self.pull_step * strength)

    def pull_right(self, strength=1.0):
        self.marker_x += int(self.pull_step * strength)

    def check_winner(self):
        if self.marker_x <= self.left_win_x:
            return "PLAYER"
        if self.marker_x >= self.right_win_x:
            return "COMPUTER"
        return None

    def reset(self):
        self.marker_x = float(self.screen_width // 2)
        self.velocity = 0.0

    def rope_points(self, tension, time_ms, segments=40):
        """Rope polyline: sags when slack, vibrates when under high tension."""
        x0, x1 = 60, self.screen_width - 60
        sag = (1.0 - tension) * 14
        amp = max(0.0, tension - 0.45) * 7
        t = time_ms / 1000.0
        pts = []
        for i in range(segments + 1):
            u = i / segments
            x = x0 + (x1 - x0) * u
            y = self.center_y + sag * 4 * u * (1 - u)
            y += amp * math.sin(u * 18 + t * 55) * math.sin(u * math.pi)
            pts.append((x, y))
        return pts

    def render(self, surface, tension=0.5, time_ms=0):
        pygame.draw.lines(
            surface, (180, 140, 90), False, self.rope_points(tension, time_ms), 10
        )

        pygame.draw.line(
            surface,
            (50, 200, 50),
            (self.left_win_x, self.center_y - 40),
            (self.left_win_x, self.center_y + 40),
            4
        )
        pygame.draw.line(
            surface,
            (200, 50, 50),
            (self.right_win_x, self.center_y - 40),
            (self.right_win_x, self.center_y + 40),
            4
        )

        pygame.draw.line(
            surface,
            (120, 120, 120),
            (self.screen_width // 2, self.center_y - 20),
            (self.screen_width // 2, self.center_y + 20),
            2
        )

        flag_rect = pygame.Rect(int(self.marker_x) - 12, self.center_y - 24, 24, 48)
        pygame.draw.rect(surface, (230, 40, 40), flag_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), flag_rect, width=2, border_radius=4)