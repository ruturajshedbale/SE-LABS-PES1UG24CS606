import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    def __init__(self, x, y, color, label):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.lean = 0.0
        self.font = pygame.font.SysFont(None, 24)

    def update(self, delta_seconds, lean_target):
        lean_target = max(-1.0, min(1.0, lean_target))
        blend = min(1.0, max(0.0, delta_seconds) * 8.0)
        self.lean += (lean_target - self.lean) * blend

    def render(self, surface):
        """Draw avatar and label."""
        lean_offset = round(self.lean * 24)
        body_points = [
            (self.x - 20 + lean_offset, self.y - 35),
            (self.x + 20 + lean_offset, self.y - 35),
            (self.x + 20, self.y + 35),
            (self.x - 20, self.y + 35),
        ]
        pygame.draw.polygon(surface, self.color, body_points)
        pygame.draw.line(surface, self.color, body_points[0], body_points[1], 6)
        pygame.draw.line(surface, self.color, body_points[1], body_points[2], 6)
        pygame.draw.line(surface, self.color, body_points[2], body_points[3], 6)
        pygame.draw.line(surface, self.color, body_points[3], body_points[0], 6)

        head_center = (self.x + lean_offset, self.y - 50)
        pygame.draw.circle(surface, (240, 210, 180), head_center, 16)

        label_surf = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label_surf, (self.x - label_surf.get_width() // 2, self.y + 45))
