import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    def __init__(self, x, y, color, label, back_dir=-1):
        # back_dir: -1 if "backward" is screen-left, +1 if screen-right
        self.back_dir = back_dir
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.font = pygame.font.SysFont(None, 24)

    def render(self, surface, lean=0.0):
        """Draw avatar and label. lean in [0, 1]: how far the puller leans
        backward (away from the rope) while holding pulling momentum."""
        shift = int(lean * 22) * self.back_dir
        feet_l, feet_r = self.x - 20, self.x + 20
        top_l, top_r = self.x - 20 + shift, self.x + 20 + shift
        top_y, bot_y = self.y - 35, self.y + 35

        # Body (leaning parallelogram, feet planted)
        pygame.draw.polygon(
            surface, self.color,
            [(top_l, top_y), (top_r, top_y), (feet_r, bot_y), (feet_l, bot_y)]
        )

        # Arm reaching toward the rope
        pygame.draw.line(
            surface, (240, 210, 180),
            (self.x + shift, self.y - 20), (self.x - self.back_dir * 30, self.y), 6
        )

        # Head
        pygame.draw.circle(
            surface, (240, 210, 180), (self.x + int(shift * 1.3), self.y - 50), 16
        )

        # Name / control tag
        label_surf = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label_surf, (self.x - label_surf.get_width() // 2, self.y + 45))