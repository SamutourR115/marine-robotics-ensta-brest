from roblib import * # numpy, matplotlib helpers

k1, k2 = 1.0, 1.0 # gains (to be identified)

def f(x, u): # x = (x, y, theta), u = (u1, u2)
    v = k2 * (u[0] + u[1]) / 2
    w = k1 * (u[1] - u[0])
    return array([v*cos(x[2]), v*sin(x[2]), w])

dt = 0.05
x = array([0., 0., 0.])
ax = init_figure(-10, 10, -10, 10)

def square(t): # 4 s straight, then turn in place pi/2 rad (w = 1 rad/s)
    return array([1., 1.]) if t % (4 + pi/2) < 4 else array([-0.5, 0.5])

tests = {1: lambda t: array([1., 1.]),   # u1 = u2
         2: lambda t: array([0.8, 1.]),  # u1 < u2
         3: lambda t: array([1., 0.8]),  # u1 > u2
         4: lambda t: array([1., -1.]),  # u1 = -u2
         5: square}

control = tests[5] # pick the question here
path = []

for k in range(600):
    u = control(k*dt) # left, right thrust
    x = x + dt * f(x, u) # Euler step
    clear(ax)
    path.append(x[:2])
    ax.plot(*array(path).T, 'b') # trail
    draw_tank(x) # draw the vehicle
    pause(0.01)

