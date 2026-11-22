# Tug of War Repair Lab

This project is a competitive tug-of-war game using **Pygame**. It introduces students to alternating keyboard input synchronization, debounce and lock state patterns, physics-based tension balancing, and autonomous AI pulling mechanics within an object-oriented codebase.
---

## Features

- Players pull left by alternating `A` and `D`; overlapping key-down events are handled independently, and key-repeat events do not create duplicate pulls.
- The computer pulls right on a timed cadence and enters a faster, stronger panic surge when the marker nears the player's goal.
- Rope sag/vibration, a tension meter, and puller leaning respond to the marker's displacement and pulling activity.
- A live match timer triggers Sudden Death after 45 seconds. Both player and computer pulls then have double strength.
- Boundary detection, the game-over overlay, and `R` to restart remain supported; restarting clears input state and resets the match timer.

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

**Controls:** Alternate `A` and `D` to pull the rope left. Press `R` after game over to start a new match.


## Lab Tasks Implemented

1. Reworked alternating input so overlapping `A`/`D` presses do not deadlock.
2. Added an adaptive computer panic surge near the player's winning boundary.
3. Added tension-based rope motion and responsive puller leaning.
4. Added a 45-second match timer and double-strength Sudden Death.

Run the unit tests with:

```bash
python -m pytest
```

---

## Expected Behavior

- Rapidly alternating between A and D reliably moves the red center flag to the left without freezing or dropping inputs during fast mashing.
- The computer pulls the marker to the right at recurring intervals.
- The match ends when the flag crosses the left boundary (Player wins) or right boundary (Computer wins).
- Pressing R on the Game Over screen resets the rope marker, keys, timers, and game states.
---

## Folder Structure

```
tug_of_war/
├── game/
│   ├── game_engine.py
│   ├── player.py
│   └── rope.py
├── main.py
└── README.md
```

---
