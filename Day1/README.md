# Autonomous boats & heading control of the virtual DD-Boat

This exercise simulates a **DD-Boat** (differential-drive boat), a small surface vessel with two thrusters and no rudder. It steers only by changing the thrust difference between the left and right motors. The boat sails in a 12 m × 20 m pool, and a heading controller takes it through a list of waypoints. The same controller is then connected to the course's **Unity virtual regatta** over UDP.

## Files

| File | Role |
|---|---|
| [ddboatlib.py](ddboatlib.py) | Course helpers: `init_figure`, `clear`, `draw_ddboat`, `draw_polygon`, `draw_disk`, `drawEllipsoid`, `sawtooth`, pool ↔ lat/long conversion |
| [simulator.py](simulator.py) | DD-Boat state model, heading controller and waypoint following |
| [client_pour_virtual_regatta.py](client_pour_virtual_regatta.py) | UDP client that receives the boat's pose from Unity and sends motor commands |

## 1. The model ([simulator.py](simulator.py))

The state is `x = (x, y, θ, v)`: position, heading (trigonometric, 0 = east, counter-clockwise) and speed. The input is `u = (u1, u2)`, the left and right thrust.

```
ẋ = v·cos θ
ẏ = v·sin θ
θ̇ = u2 − u1          more thrust on the right turns the boat left
v̇ = (u1 + u2) − v     the total thrust drives the speed, the drag is linear
```

The model is integrated with an Euler step: `x ← x + dt·f(x, u)`, with `dt = 0.05` s, for 30 s.

## 2. The heading controller

```python
def control(x, θd, v0=1.2, Kp=2.0):
    e = sawtooth(θd - x[2, 0])          # heading error in [-π, π]
    return [[v0 - Kp*e], [v0 + Kp*e]]   # (u1, u2)
```

- `v0` is the cruise thrust shared by both motors.
- `Kp·e` is added on one side and removed on the other. If `e > 0`, the boat must turn left (counter-clockwise), so `u2 > u1`.
- **`sawtooth` is essential.** Without it, a target at +179° and a heading of −179° would give an error of 358° instead of −2°, and the boat would turn the long way round.

## 3. Waypoint following

```python
waypoints = [(9.5, 16.0), (3.5, 16.0), (3.5, 6.0)]
```

At each step the desired heading points at the current waypoint: `θd = atan2(y_wp − y, x_wp − x)`. When the boat is closer than **1.2 m**, it moves on to the next waypoint. After the last one, both motors are set to 0.

## 4. Virtual regatta client ([client_pour_virtual_regatta.py](client_pour_virtual_regatta.py))

The Unity simulator publishes the pose of every boat and accepts JSON commands over UDP:

| Direction | Port | Message |
|---|---|---|
| client → Unity | 5005 | `{"id", "password", "reset": true}` once, then `{"id", "password", "cmd_left", "cmd_right"}` |
| Unity → client | 5006 | `{"id", "X", "Y", "heading_deg"}` for every boat. The client keeps only its own `ROBOT_ID` |

## Running

```bash
pip install numpy matplotlib
python simulator.py                       # pool simulation
python client_pour_virtual_regatta.py     # needs Unity on the network, set UNITY_IP and ROBOT_ID first
```

## Known limitations / gotchas

- **Importing `simulator` runs it.** `simulator.py` has no `if __name__ == "__main__":` guard, so `from simulator import control` in the client first plays the full 30 s simulation.
- **The client ignores its controller.** It calls `control(...)` but throws the result away and always sends `cmd_left = cmd_right = 5`. Its target `atan2(Y − x[1], X − x[0])` is also always 0, because `x` is built from the same `X` and `Y`.
- **Heading conventions.** This simulator uses the trigonometric convention. The real boat (Day 3) uses a compass heading (0 = north, clockwise), so the sign of the steering term flips there.
