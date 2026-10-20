import numpy as np
import matplotlib.pyplot as plt
from ddboatlib import init_figure, clear, draw_ddboat, sawtooth

def f(x, u):
    xr, yr, θr, vr = x.flatten()
    u1, u2 = u.flatten()
    xr_dot = vr * np.cos(θr)
    yr_dot = vr * np.sin(θr)
    θr_dot = u2 - u1
    vr_dot = (u1 + u2) - vr
    return np.array([[xr_dot], [yr_dot], [θr_dot], [vr_dot]])

def control(x, θd, v0=1.2, Kp=2.0):
    θr = x[2, 0]
    e = sawtooth(θd - θr)
    return np.array([[v0 - Kp * e], [v0 + Kp * e]])

waypoints = [(9.5, 16.0), (3.5, 16.0), (3.5, 6.0)]
wp = 0

ax = init_figure(-1, 13, -1, 21)
dt = 0.05
x = np.array([[7.0], [2.0], [0.9], [0.5]])

for t in np.arange(0, 30, dt):
    clear(ax)
    xr, yr, θr, vr = x.flatten()

    if wp < len(waypoints) and np.hypot(waypoints[wp][0] - xr, waypoints[wp][1] - yr) < 1.2:
        wp += 1

    if wp < len(waypoints):
        θd = np.arctan2(waypoints[wp][1] - yr, waypoints[wp][0] - xr)
        u = control(x, θd)
    else:
        u = np.array([[0.0], [0.0]])

    x = x + dt * f(x, u)
    draw_ddboat(ax, xr, yr, θr, u[0, 0], u[1, 0], True, "red")
    plt.pause(0.01)