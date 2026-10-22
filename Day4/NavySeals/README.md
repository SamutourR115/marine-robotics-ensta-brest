# Team NavySeals: Day 4, Ground Station and Regatta

Day 4 builds on the [Day 3 project](../../Day3/NavySeals/README.md). The race controller now scores real gate crossings, the keyboard teleop is easier to drive, and a **ground station GUI** on the laptop switches the boat between remote control and autonomous mode with one click.

The boat scripts still run **on the boat** (Raspberry Pi 3, Python 3.5.3, no f-strings) with the course drivers `arduino_driver_v2`, `gps_driver_v2` and `imu9_driver_v2`, which are not in this repository. Only `boat_gui.py` runs on the laptop.

## What changed since Day 3

| File | Change |
|---|---|
| [boat_gui.py](boat_gui.py) | **New.** Laptop GUI: RC / autonomous switch, STOP, live instruments, boat terminal |
| [regatta_loop.py](regatta_loop.py) | Gates read from a JSON file, real ±1 scoring of gate segment crossings, safety checks before the start |
| [regatta_gates.example.json](regatta_gates.example.json) | **New.** Gate file template: two endpoints (lat, lon) and the +1 direction per gate |
| [rc_teleop.py](rc_teleop.py) | Commands latch (press once, the boat keeps going until Space), 5 s watchdog, ESC deadband compensation |
| [waypoint_mission.py](waypoint_mission.py) | Reads the freshest GPS fix, rejects empty fixes, pivots with hysteresis, validates a waypoint once its line is passed |
| [simu_page13.py](simu_page13.py), [digital_twin_exercises.py](digital_twin_exercises.py), [DIGITAL_TWIN.md](DIGITAL_TWIN.md) | **New.** Digital twin exercises (straight line, turn direction, pivot, square) and notes |
| [calib_boat11.json](calib_boat11.json) | Compass calibration of boat 11, required by the controllers |

The other scripts (`stop.py`, `calib.py`, `gps.py`, `battery*.py`, `heading_hold.py`, `control.py`, …) are unchanged; see the [Day 3 README](../../Day3/NavySeals/README.md).

## 1. Ground station GUI ([boat_gui.py](boat_gui.py))

```
┌ DD-BOAT 11  ● RC TELEOP  ue32@172.20.25.211 ─────────────── [ STOP ] ┐
│ ┌ control panel ───────────┐ ┌ TERMINAL ───────────────────────────┐ │
│ │ [RC teleop] [Autonomous] │ │ $ ssh ue32@… 'python3 stop.py'      │ │
│ │  compass        L   R    │ │ >> MOTORS STOPPED (0, 0) <<         │ │
│ │  heading+target ▮   ▮    │ │ $ ssh ue32@… 'python3 rc_teleop.py' │ │
│ │ Action  │ Speed          │ │ ...                                 │ │
│ │ Battery │ Target         │ │                                     │ │
│ │ Distance│ Score          │ │                                     │ │
│ │ Laps    │ Time left      │ │                                     │ │
│ │      ▲                   │ │                                     │ │
│ │    ◀ ■ ▶                 │ │                                     │ │
│ │      ▼                   │ │                                     │ │
│ │ Slow Med Fast − +        │ │                                     │ │
│ └──────────────────────────┘ └─────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

- **RC teleop** starts `rc_teleop.py`. Keyboard (WASD, arrows, Space, `+`/`-`, `1`/`2`/`3`) or the on-screen pad drive the boat. The motor bars show the left and right commands.
- **Autonomous** starts `regatta_loop.py` (change `AUTO_CMD` to run another mission). The compass shows the heading (blue) and the direction of the target (green, dashed). The tiles show the target, distance, score, laps and time left.
- **STOP** stops the running script and sets both thrusters to 0.

The GUI does not change anything on the boat. It starts the existing scripts over SSH with `ssh -tt`, so they get a real terminal, and reads their output to fill the panel. **Every switch stops the current script first**: Ctrl+C makes its `finally` block send `(0, 0)` and save the KML, then `stop.py` runs as a backup. The next mode starts only once the motors are at zero.

```bash
python3 boat_gui.py                              # boat = ue32@172.20.25.211
BOAT=best@172.20.25.211 python3 boat_gui.py      # other account or boat
```

Start it from a terminal: the SSH password is asked there, once, because all commands share one SSH connection. `ssh-copy-id ue32@172.20.25.211` removes the prompt. Requirements on the laptop: Python 3 with Tkinter and an `ssh` client.

## 2. Regatta controller ([regatta_loop.py](regatta_loop.py))

Each gate is a **segment** between two buoys, with a `plus_heading_deg` that tells which crossing direction scores +1.

1. **Course.** For every gate, an entry waypoint is placed 4 m before its middle and an exit waypoint 4 m after it. The boat loops `entry A → exit A → entry B → exit B → …`.
2. **Checks before the start.** The script refuses to race without `calib_boat11.json` or a valid gate file. It also refuses if a gate is shorter than 0.5 m, if its +1 direction is almost parallel to it, if it is more than 200 m from the launch point, or if a transit leg passes within 1 m of another gate, since that leg would score −1.
3. **Scoring.** Each new GPS position is joined to the previous one, and the score changes only when that step really crosses a gate segment: +1 in the right direction, −1 the other way.
4. **Steering.** The boat pivots in place when the heading error is above 40° and cruises again below 20° (hysteresis). Otherwise it uses the sawtooth law `u = 75 ± 30·e`. A waypoint is validated within 2.5 m, or once its line is passed.
5. **Safety and logs.** Motors are cut if the GPS fix is lost for 3 s. The race stops after 5 minutes. `regatta_log.csv` and `regatta_track.kml` (track + gates) are written for the jury.

```bash
cp regatta_gates.example.json regatta_gates.json   # then enter the real gate coordinates
python3 regatta_loop.py                            # or: python3 regatta_loop.py my_gates.json
```

The Day 3 limitations are fixed: gates are no longer hard-coded, the crossing direction is checked, and the mission plan names the right script.

## Known limitations

- **Wi-Fi loss in autonomous mode.** If the SSH link drops, the remote script is killed without running its `finally` block, so the thrusters may keep their last command. Keep `stop.py` ready on another device.
- **Arrow keys in `rc_teleop.py` over plain SSH.** The script reads the first byte of an arrow key, but Python has already buffered the rest, so the arrow is read as Escape and ignored. The GUI sends WASD instead. Over plain SSH, use WASD.
- **The GUI freezes about 1 to 2 s on STOP or on a mode switch**, while `stop.py` runs on the boat. This is on purpose: the next mode only starts once the motors are at zero.
- **No motor bars in autonomous mode.** `regatta_loop.py` writes its motor commands to the CSV log but does not print them.
- **Windows.** SSH connection sharing is disabled on Windows (OpenSSH does not support it), so the password may be asked at each switch.
- **Not yet tested on the water.** The GUI was tested on macOS against a simulated boat (local stand-ins for SSH and the drivers), not on boat 11 itself.
- **Notes not in the repo.** `PROJECT_RECORD.md` and `SESSION_HANDOVER.md` are in `.gitignore` because they contain the boat's network credentials.
