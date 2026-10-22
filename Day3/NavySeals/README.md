# Team NavySeals: DD-Boat 11 on Lake Guerlédan

On Day 3 the teams were formed and the project started. Team **NavySeals** works on **DD-Boat 11**, a real differential-drive boat. The goal is to bring it from a first hardware check to autonomous navigation, and then to the **Friday regatta**: 5 minutes, +1 point for each gate crossed in the right direction, −1 otherwise.

## The boat

| Part | Details |
|---|---|
| Computer | Raspberry Pi 3, Raspbian Stretch, **Python 3.5.3** |
| Motors | 2 brushless thrusters and their ESCs, driven by an Arduino MEGA (`/dev/ttyACM0`, 115200 baud), commands in `[-255, 255]` |
| IMU | Pololu 9-DOF v5 on I2C: magnetometer LIS3MDL, accelerometer + gyroscope LSM6DS33 |
| GPS | NMEA receiver, `GPGLL` sentences at 1 Hz |
| Battery | 2 × 2S LiPo (7.4 V nominal). Stop below 7.5 V, use more than 8.0 V for long runs |
| Radio | Switch F up = manual radio control, down = Python control |

The scripts run **on the boat**, over SSH. They use the course drivers `arduino_driver_v2`, `gps_driver_v2` and `imu9_driver_v2`, which are installed on the boat and are not in this repository.

## Files

| Step | File | Role |
|---|---|---|
| Safety | [stop.py](stop.py) | Sets both thrusters to 0. Keep a terminal ready with it |
| Check | [boat11_smoke_test.py](boat11_smoke_test.py) | Tests the Arduino (short motor pulse), the IMU and the GPS |
| Check | [motor_test.py](motor_test.py) | Turns in place for 2 s (left = 100, right = −100), then stops |
| Sensors | [calib.py](calib.py) | Compass calibration and live heading display |
| Sensors | [gps.py](gps.py) | Reads the GPS, projects to UTM zone 30N, writes `gps_data.kml` for Google Earth |
| Battery | [battery.py](battery.py), [battery_monitor.py](battery_monitor.py), [battery_probe.py](battery_probe.py) | Estimated state of charge, and a probe looking for a voltage source on the boat |
| Control | [heading_hold.py](heading_hold.py) | Holds a compass heading |
| Control | [waypoint_mission.py](waypoint_mission.py) | Follows a list of GPS waypoints and logs to `mission_log.csv` |
| Control | [control.py](control.py) | Return-to-home: `boomerang` (out and back) or `rth_gps` |
| Control | [rc_teleop.py](rc_teleop.py) | Keyboard driving over SSH (WASD, arcade mixing) with a 1 s watchdog |
| Race | [regatta_loop.py](regatta_loop.py) | Goes A → B → A… for 5 minutes, counts the gates, logs to CSV and KML |
| Docs | [COMPASS_CALIBRATION_REPORT.md](COMPASS_CALIBRATION_REPORT.md), [REGATTA_MISSION_PLAN.md](REGATTA_MISSION_PLAN.md) | Calibration results and race strategy |

## 1. Compass calibration ([calib.py](calib.py))

The magnetometer is distorted by the boat itself. Metal parts and currents shift the measured field (**hard iron**, offset `b`) and stretch it (**soft iron**, matrix `A`). The boat is turned slowly through two full circles, and a circle is fitted to the raw points:

```
m_calib = A⁻¹ · (m_raw − b)
heading = (90° − atan2(m_y, m_x)) mod 360°      0° = north, clockwise
```

`scipy` is not installed on the boat, so the fit uses only `numpy.linalg`. The result is saved to `calib_boat11.json`. When checked against a compass, the error was at most **1.5°** on the four cardinal directions (see the [report](COMPASS_CALIBRATION_REPORT.md)).

## 2. From GPS to metres

Every controller converts latitude and longitude into a local frame in metres (x = east, y = north) around the course reference point **48.199111° N, −3.014930° E**. Then distance and bearing to a target are simple:

```
d = √(dx² + dy²)
θ_target = (90° − atan2(dy, dx)) mod 360°
```

## 3. Steering law

This is the same idea as Day 1, but with a **compass** heading, which is clockwise:

```
e  = sawtooth(θ_target − θ)
u1 = clip(v0 + Kp·e)      left thruster
u2 = clip(v0 − Kp·e)      right thruster
```

If `e > 0`, the boat must turn right, so the left motor pushes harder. That is the opposite sign of Day 1, because the angle now turns the other way. The first on-water logs showed a 180° error caused by this exact sign mistake, and it was then fixed in every controller.

| Script | `v0` | `Kp` | Arrival radius |
|---|---|---|---|
| `heading_hold.py` | 45 (argument) | 35 | n/a |
| `control.py` | 40 (argument) | 35 | 2 m (`rth_gps`) |
| `waypoint_mission.py` | 45 | 40 | 2.5 m |
| `regatta_loop.py` | 55 | 35 | 3 m |

## Running

```bash
ssh ue32@172.20.25.211        # boat 11
cd ~/NavySeals

python3 stop.py                          # always first, in a second terminal
python3 boat11_smoke_test.py
python3 calib.py                         # press T for the live check
python3 heading_hold.py 90 40 10         # heading, speed, duration (s)
python3 control.py boomerang 120 40 30   # out on 120° for 15 s, back for 15 s
python3 regatta_loop.py
```

Before sending commands, wait until the ESCs have played their start-up tune 3 times. Before that, they ignore commands.

## Known limitations / gotchas

- **Python 3.5.3**: no f-strings on the boat. Use `.format()`.
- **Outdated docstring**: the docstring of `heading_hold.py` still shows the old sign (`u1 = v0 − Kp·e`). The code itself uses the corrected one.
- **Gates are placeholders**: `regatta_loop.py` uses `(15, 10)` and `(35, 30)` m. Replace them with the real gate positions on race day.
- **"Crossing" means "came within 3 m"**: the direction of crossing is not checked, so a −1 crossing would still be counted as +1.
- **The plan names the wrong script**: [REGATTA_MISSION_PLAN.md](REGATTA_MISSION_PLAN.md) says to launch `waypoint_mission.py` for the race, but the race controller is `regatta_loop.py`.
- **The battery level is an estimate**: `battery.py` counts the charge used from motor commands and time, assuming a 5000 mAh pack. It does not measure the voltage. `battery_state.json` is that script's saved state.
- **Notes not in the repo**: `PROJECT_RECORD.md` and `SESSION_HANDOVER.md` are in `.gitignore` because they contain the boat's network credentials.
