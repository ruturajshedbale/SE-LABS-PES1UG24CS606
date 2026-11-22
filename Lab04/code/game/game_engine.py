import random

import pygame

from game.rope import Rope
from game.player import Puller


class GameEngine:
    NORMAL_PULL_INTERVAL_MS = 180
    PANIC_PULL_INTERVAL_MS = 60
    PANIC_DISTANCE_RATIO = 0.35
    MATCH_DURATION_MS = 45_000
    SUDDEN_DEATH_MULTIPLIER = 2.0

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)")
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER")

        self.last_key = None
        self.held_keys = set()
        self.winner = None
        self.game_state = "PLAYING"
        self.panic_mode = False
        self.sudden_death = False

        self.computer_pull_cooldown = self.NORMAL_PULL_INTERVAL_MS
        now = pygame.time.get_ticks()
        self.last_computer_pull = now
        self.last_update_time = now
        self.match_start_time = now
        self.match_elapsed_ms = 0

        self.font_big = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if event.type == pygame.KEYUP:
            self.held_keys.discard(event.key)
            return

        if event.type != pygame.KEYDOWN:
            return

        if self.game_state != "PLAYING":
            if event.key == pygame.K_r:
                self.reset()
            return

        if event.key not in (pygame.K_a, pygame.K_d) or event.key in self.held_keys:
            return

        self.held_keys.add(event.key)
        if event.key != self.last_key:
            strength = self.SUDDEN_DEATH_MULTIPLIER if self.sudden_death else 1.0
            self.rope.pull_left(strength)
            self.last_key = event.key

    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        delta_ms = max(0, now - self.last_update_time)
        self.last_update_time = now
        self.match_elapsed_ms = max(0, now - self.match_start_time)
        if self.match_elapsed_ms >= self.MATCH_DURATION_MS:
            self.sudden_death = True

        center_x = self.width // 2
        player_range = max(1, center_x - self.rope.left_win_x)
        player_progress = (center_x - self.rope.marker_x) / player_range
        player_progress = max(-1.0, min(1.0, player_progress))
        self.rope.update_tension(delta_ms / 1000, abs(player_progress))
        self.player.update(delta_ms / 1000, -player_progress)
        self.computer.update(delta_ms / 1000, player_progress)

        distance_to_player_goal = self.rope.marker_x - self.rope.left_win_x
        self.panic_mode = (
            distance_to_player_goal <= player_range * self.PANIC_DISTANCE_RATIO
        )
        self.computer_pull_cooldown = (
            self.PANIC_PULL_INTERVAL_MS if self.panic_mode else self.NORMAL_PULL_INTERVAL_MS
        )

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"
            return

        if now - self.last_computer_pull >= self.computer_pull_cooldown:
            if self.panic_mode:
                computer_strength = random.uniform(1.8, 2.4)
            else:
                computer_strength = random.uniform(0.7, 1.2)
            if self.sudden_death:
                computer_strength *= self.SUDDEN_DEATH_MULTIPLIER
            self.rope.pull_right(computer_strength)
            self.last_computer_pull = now

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def reset(self):
        self.rope.reset()
        self.last_key = None
        self.held_keys.clear()
        self.winner = None
        self.game_state = "PLAYING"
        now = pygame.time.get_ticks()
        self.last_computer_pull = now
        self.last_update_time = now
        self.match_start_time = now
        self.match_elapsed_ms = 0
        self.sudden_death = False
        self.panic_mode = False

    def render(self, screen):
        screen.fill((30, 32, 36))

        timer_text = (
            f"TIME {self.match_elapsed_ms // 60_000:02d}:"
            f"{(self.match_elapsed_ms // 1000) % 60:02d}"
        )
        timer_color = (255, 205, 90) if self.sudden_death else (225, 225, 225)
        timer_surface = self.font_small.render(timer_text, True, timer_color)
        screen.blit(timer_surface, (self.width // 2 - timer_surface.get_width() // 2, 8))

        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        now = pygame.time.get_ticks()
        self.rope.render(screen, now)
        self.player.render(screen)
        self.computer.render(screen)

        inst_surf = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, 40))

        tension_width = int(120 * self.rope.tension)
        pygame.draw.rect(screen, (80, 80, 80), (self.width - 150, 16, 120, 12), border_radius=6)
        pygame.draw.rect(
            screen,
            (235, 155, 65),
            (self.width - 150, 16, tension_width, 12),
            border_radius=6,
        )
        tension_label = self.font_small.render("TENSION", True, (210, 210, 210))
        screen.blit(tension_label, (self.width - 150, 32))

        if self.panic_mode and self.game_state == "PLAYING":
            panic_surface = self.font_small.render(
                "COMPUTER PANIC SURGE!", True, (255, 115, 80)
            )
            screen.blit(
                panic_surface,
                (self.width // 2 - panic_surface.get_width() // 2, 72),
            )

        if self.sudden_death and self.game_state == "PLAYING":
            sudden_surface = self.font_small.render(
                "SUDDEN DEATH - DOUBLE PULL POWER", True, (255, 205, 90)
            )
            screen.blit(
                sudden_surface,
                (self.width // 2 - sudden_surface.get_width() // 2, 100),
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
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 50),
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10),
            )
