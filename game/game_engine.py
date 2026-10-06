import random
import pygame
from game.rope import Rope
from game.player import Puller


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)")
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER", back_dir=1)

        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

        # Pulling momentum in [-1, 1]: negative = player winning the struggle
        self.momentum = 0.0

        self.sudden_death_ms = 45_000
        self.sudden_death = False
        self.match_start = pygame.time.get_ticks()
        self.elapsed_ms = 0

        self.base_pull_cooldown = 180
        self.panic_pull_cooldown = 85
        self.computer_pull_cooldown = self.base_pull_cooldown
        self.panic_active = False
        self.last_computer_pull = pygame.time.get_ticks()

        self.font_big = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        # A pull registers on every KEYDOWN that differs from the previous
        # pulling key. No release-based lock, so overlapping presses can
        # never freeze input.
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_a, pygame.K_d):
            if event.key != self.last_key:
                self.rope.pull_left(1.0 * self.power_multiplier())
                self.momentum = max(-1.0, self.momentum - 0.3)
                self.last_key = event.key

    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        self.elapsed_ms = now - self.match_start
        self.sudden_death = self.elapsed_ms >= self.sudden_death_ms
        self.update_panic()
        if now - self.last_computer_pull >= self.computer_pull_cooldown:
            if self.panic_active:
                computer_variance = random.uniform(1.4, 2.0)
            else:
                computer_variance = random.uniform(0.7, 1.2)
            self.rope.pull_right(computer_variance * self.power_multiplier())
            self.momentum = min(1.0, self.momentum + 0.3 * computer_variance)
            self.last_computer_pull = now

        self.momentum *= 0.95

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def power_multiplier(self):
        """Sudden death doubles pulling power for every action."""
        return 2.0 if self.sudden_death else 1.0

    def update_panic(self):
        """Panic surge: once the marker is pulled 40% of the way from center
        to the player's goal, the computer pulls faster and harder."""
        mid = self.width // 2
        threshold = mid - (mid - self.rope.left_win_x) * 0.4
        self.panic_active = self.rope.marker_x <= threshold
        self.computer_pull_cooldown = (
            self.panic_pull_cooldown if self.panic_active else self.base_pull_cooldown
        )

    def reset(self):
        self.rope.reset()
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.last_computer_pull = pygame.time.get_ticks()
        self.panic_active = False
        self.computer_pull_cooldown = self.base_pull_cooldown
        self.momentum = 0.0
        self.match_start = pygame.time.get_ticks()
        self.elapsed_ms = 0
        self.sudden_death = False

    def tension(self):
        """0 = slack rope, 1 = maximum strain (struggle intensity)."""
        offset = abs(self.rope.marker_x - self.width // 2)
        reach = self.width // 2 - self.rope.left_win_x
        return min(1.0, 0.6 * min(1.0, offset / reach) + 0.7 * abs(self.momentum))

    def render(self, screen):
        screen.fill((30, 32, 36))

        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        self.rope.render(screen, self.tension(), pygame.time.get_ticks())
        self.player.render(screen, lean=max(0.0, -self.momentum))
        self.computer.render(screen, lean=max(0.0, self.momentum))

        secs = self.elapsed_ms // 1000
        timer_surf = self.font_big.render(
            f"{secs // 60:02d}:{secs % 60:02d}", True, (240, 240, 240)
        )
        screen.blit(timer_surf, (self.width // 2 - timer_surf.get_width() // 2, 4))
        if self.sudden_death:
            sd_surf = self.font_small.render(
                "SUDDEN DEATH - DOUBLE POWER!", True, (255, 60, 60)
            )
            screen.blit(sd_surf, (self.width // 2 - sd_surf.get_width() // 2, 68))

        inst_surf = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, 44))

        if self.panic_active and self.game_state == "PLAYING":
            panic_surf = self.font_small.render(
                "COMPUTER PANIC SURGE!", True, (255, 120, 60)
            )
            screen.blit(
                panic_surf, (self.width - panic_surf.get_width() - 20, self.height - 40)
            )

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            win_text = f"{self.winner} WINS!"
            color = (80, 220, 80) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 50)
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )
