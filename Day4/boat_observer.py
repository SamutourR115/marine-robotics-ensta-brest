#Exemple: send a command to the boat, receive a measurement and run an observer on it
from roblib import *
import socket

BOAT_IP, PORT = "192.168.1.50", 5005 # adapt

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.settimeout(0.1) # never wait forever

k1, k2 = 1.0, 1.0 # gains (to be identified), same model as sim_digital_twin.py

def f(x, u): # x = (x, y, theta), u = (u1, u2)
    v = k2 * (u[0] + u[1]) / 2
    w = k1 * (u[1] - u[0])
    return array([v*cos(x[2]), v*sin(x[2]), w])

def encode(u): # (u1, u2) -> b"0.5,0.3"
    return ",".join(str(ui) for ui in u).encode()

def decode(data): # b"x,y,theta" -> array([x, y, theta])
    return array([float(s) for s in data.decode().split(",")])

dt = 0.1 # = socket timeout, one step per loop
L = diag([2., 2., 2.]) # observer gains: to be tuned
xhat = array([0., 0., 0.]) # estimate
ax = init_figure(-10, 10, -10, 10)

while True:
    u = array([0.5, 0.3]) # command (u1, u2)
    sock.sendto(encode(u), (BOAT_IP, PORT))
    y = None
    try:
        data, _ = sock.recvfrom(1024)
        y = decode(data) # measured (x, y, theta)
        err = y - xhat
        err[2] = sawtooth(err[2]) # angle error in [-pi, pi]
    except socket.timeout:
        err = zeros(3) # no measurement: model only
    xhat = xhat + dt * (f(xhat, u) + L @ err)

    clear(ax)
    draw_tank(xhat, 'blue') # estimate
    if y is not None:
        draw_tank(y, 'red') # measurement
    pause(0.001)
