import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

import game.game_engine as game_engine
from game.game_engine import GameEngine
from game.player import Puller
from game.rope import Rope


@pytest.fixture(scope="module", autouse=True)
def pygame_setup():
    pygame.init()
    yield
    pygame.quit()


def key_event(event_type, key):
    return pygame.event.Event(event_type, key=key)


def make_engine(monkeypatch, now=0):
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: now)
    return GameEngine(800, 450)


def test_overlapping_alternating_presses_do_not_deadlock(monkeypatch):
    engine = make_engine(monkeypatch)
    start = engine.rope.marker_x

    engine.handle_event(key_event(pygame.KEYDOWN, pygame.K_a))
    engine.handle_event(key_event(pygame.KEYDOWN, pygame.K_d))
    engine.handle_event(key_event(pygame.KEYUP, pygame.K_a))
    engine.handle_event(key_event(pygame.KEYUP, pygame.K_d))
    engine.handle_event(key_event(pygame.KEYDOWN, pygame.K_a))

    assert engine.rope.marker_x == start - 3 * engine.rope.pull_step


def test_held_key_repeat_does_not_create_duplicate_pulls(monkeypatch):
    engine = make_engine(monkeypatch)
    start = engine.rope.marker_x

    engine.handle_event(key_event(pygame.KEYDOWN, pygame.K_a))
    engine.handle_event(key_event(pygame.KEYDOWN, pygame.K_a))
    engine.handle_event(key_event(pygame.KEYDOWN, pygame.K_a))

    assert engine.rope.marker_x == start - engine.rope.pull_step


def test_panic_surge_uses_faster_cadence_and_stronger_pull(monkeypatch):
    engine = make_engine(monkeypatch, now=1_000)
    engine.rope.marker_x = 250
    engine.last_computer_pull = 0
    monkeypatch.setattr(game_engine.random, "uniform", lambda _low, _high: 2.0)

    engine.update()

    assert engine.panic_mode
    assert engine.computer_pull_cooldown == engine.PANIC_PULL_INTERVAL_MS
    assert engine.rope.marker_x == 274


def test_tension_and_puller_lean_are_bounded_and_renderable():
    pygame.display.set_mode((800, 450))
    surface = pygame.Surface((800, 450))
    rope = Rope(800, 450)
    player = Puller(90, 225, (50, 120, 220), "PLAYER")

    rope.pull_left(2)
    rope.update_tension(0.1, 0.8)
    player.update(0.1, -1.0)
    rope.render(surface, now_ms=100)
    player.render(surface)

    assert 0 < rope.tension <= 1
    assert player.lean < 0
    assert -1 <= player.lean <= 1


def test_sudden_death_starts_after_45_seconds_and_doubles_player_pull(monkeypatch):
    engine = make_engine(monkeypatch, now=0)
    engine.last_computer_pull = 45_001
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 45_000)

    engine.update()
    start = engine.rope.marker_x
    engine.handle_event(key_event(pygame.KEYDOWN, pygame.K_a))

    assert engine.sudden_death
    assert engine.match_elapsed_ms == engine.MATCH_DURATION_MS
    assert engine.rope.marker_x == start - 2 * engine.rope.pull_step


def test_sudden_death_doubles_computer_pull(monkeypatch):
    engine = make_engine(monkeypatch, now=1_000)
    engine.sudden_death = True
    engine.last_computer_pull = 0
    monkeypatch.setattr(game_engine.random, "uniform", lambda _low, _high: 1.0)

    engine.update()

    assert engine.rope.marker_x == 400 + 2 * engine.rope.pull_step


def test_reset_clears_input_match_and_animation_state(monkeypatch):
    engine = make_engine(monkeypatch, now=100)
    engine.held_keys.add(pygame.K_a)
    engine.last_key = pygame.K_a
    engine.sudden_death = True
    engine.panic_mode = True
    engine.rope.pull_left()
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 500)

    engine.reset()

    assert engine.rope.marker_x == 400
    assert engine.rope.tension == 0
    assert engine.held_keys == set()
    assert engine.last_key is None
    assert not engine.sudden_death
    assert not engine.panic_mode
    assert engine.match_start_time == 500
    assert engine.match_elapsed_ms == 0
