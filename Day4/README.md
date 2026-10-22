# Digital twins of the DD-Boat

A **digital twin** is a model of the boat that runs alongside the real one and stays synchronised with it using the boat's measurements. A plain simulation runs on its own. This exercise has two parts:

1. build a simple model and check that it behaves like the boat for some test commands,
2. connect it to the boat over UDP and correct it with the measurements, using an **observer**.

## Files

| File | Role |
|---|---|
| [sim_digital_twin.py](sim_digital_twin.py) | Boat model and 5 open-loop test commands |
| [boat_observer.py](boat_observer.py) | Sends a command to the boat, receives its pose and runs an observer |
| `roblib` (pip package) | Course helpers (`init_figure`, `clear`, `draw_tank`, `sawtooth`, numpy) |

## 1. The model ([sim_digital_twin.py](sim_digital_twin.py))

The state is `x = (x, y, θ)` and the input is `u = (u1, u2)`, the left and right thrust:

```
v = k2 · (u1 + u2) / 2      forward speed: mean thrust
ω = k1 · (u2 − u1)          rotation speed: thrust difference
ẋ = v·cos θ,  ẏ = v·sin θ,  θ̇ = ω
```

`k1` and `k2` are set to 1 for now. They are the parameters to **identify** on the real boat, for example by measuring its speed with both motors equal and its turn rate in a pivot.

The model is integrated with an Euler step (`dt = 0.05` s, 600 steps = 30 s), and the trail is drawn as the boat moves.

### Test commands

Pick one with `control = tests[n]`:

| # | Command | Expected behaviour |
|---|---|---|
| 1 | `u1 = u2 = 1` | straight line |
| 2 | `u1 = 0.8 < u2 = 1` | circle to the left (counter-clockwise) |
| 3 | `u1 = 1 > u2 = 0.8` | circle to the right (clockwise) |
| 4 | `u1 = 1, u2 = −1` | spins in place to the right, no forward motion |
| 5 | square | 4 s straight, then `(−0.5, 0.5)` for π/2 s: ω = 1 rad/s, so a 90° turn to the left |

If the real boat does the same thing for the same commands, the model's structure is right. Then only `k1` and `k2` need adjusting.

## 2. The observer ([boat_observer.py](boat_observer.py))

At each step the script:

1. sends the command `u` to the boat over UDP as text (`b"0.5,0.3"`),
2. waits at most 0.1 s for a measurement `y = (x, y, θ)` (`b"x,y,theta"`),
3. updates the estimate `x̂`:

```
x̂ ← x̂ + dt · ( f(x̂, u) + L · (y − x̂) )
```

- `f(x̂, u)` is the **prediction**: where the model thinks the boat goes.
- `L · (y − x̂)` is the **correction**: it pulls the estimate towards the measurement. Larger gains in `L` trust the sensors more, smaller ones trust the model more.
- The heading error goes through `sawtooth`, so an error of 359° counts as −1°.
- If no measurement arrives before the timeout, the correction is 0 and the twin runs on the model alone. This is what keeps it useful when the link drops.

The estimate is drawn in blue and the measurement in red.

## Running

```bash
pip install roblib
python sim_digital_twin.py     # choose the test with control = tests[n]
python boat_observer.py        # set BOAT_IP and PORT first
```

## Known limitations / gotchas

- **`dt` is assumed, not measured.** The observer uses `dt = 0.1` because that is the socket timeout. If the boat replies faster, each loop is shorter than 0.1 s and the model moves too fast. Measuring the real time between steps with `time.time()` would fix this.
- **Fixed command and placeholder address.** The command is always `(0.5, 0.3)`, and `BOAT_IP = "192.168.1.50"` is only an example.
- **The gains are not tuned.** `k1 = k2 = 1` and `L = diag(2, 2, 2)` are starting values. With `dt = 0.1`, the correction stays stable as long as `L·dt < 2`.
- **The model is duplicated.** The same `f` is copied into both scripts. If you change it in one, change it in the other.
