#!/usr/bin/env python3
"""
DD-Boat 11 - Ground Station GUI (runs on the LAPTOP, not on the boat)
=====================================================================
Left: control panel (mode switch, compass, motor bars, live stats, D-pad).
Right: the boat's terminal output.

  RC teleop   runs rc_teleop.py; WASD / arrows / Space / + / - / 1 2 3
              (keyboard or on-screen pad) are forwarded to the boat.
  Autonomous  runs AUTO_CMD (regatta_loop.py by default).
  STOP        Ctrl+C to the running script, then stop.py -> motors (0, 0).

Every switch first stops the current script (Ctrl+C so its finally block
zeroes the motors and saves the KML), then runs stop.py as a backup.
Nothing changes on the boat: the existing scripts are started over SSH.

Usage:
    python3 boat_gui.py                      # boat = ue32@172.20.25.211
    BOAT=best@172.20.25.211 python3 boat_gui.py

Launch it from a terminal: the SSH password is asked there
(or run `ssh-copy-id ue32@172.20.25.211` to never type it).
"""

import math
import os
import queue
import re
import subprocess
import threading
import time
import tkinter as tk

BOAT = os.environ.get("BOAT", "ue32@172.20.25.211")
REMOTE_DIR = "~/NavySeals"
AUTO_CMD = "python3 regatta_loop.py"
MODES = {"RC": "python3 rc_teleop.py", "AUTO": AUTO_CMD}

SSH = ["ssh", "-o", "ConnectTimeout=5"]
if os.name != "nt":  # one shared connection: password asked once, fast switching (not on Windows OpenSSH)
    SSH += ["-o", "ControlMaster=auto", "-o", "ControlPath=~/.ssh/ddboat-%C", "-o", "ControlPersist=300"]
SSH += [BOAT]

# Send arrows as WASD: rc_teleop's escape-code parsing misses arrows (stdin buffering eats "[C")
ARROWS = {"Up": "w", "Down": "s", "Right": "d", "Left": "a"}

# Status lines printed by rc_teleop.py and regatta_loop.py
RC_LINE = re.compile(r"\[([^\]]+)\]\s*Spd:\s*(\d+)\s*\|\s*L:\s*([+-]?\d+)\s*R:\s*([+-]?\d+)\s*\|\s*Batt:\s*(\S+)")
AUTO_LINE = re.compile(r"Rem:\s*(\d+)s\]\s*->\s*(.+?)\s*\|\s*Dist:\s*([\d.]+)m\s*\|\s*Score:\s*(-?\d+)\s*\|"
                       r"\s*Laps:\s*(\d+)\s*\|\s*Hdg:\s*([\d.]+)\S*\s*\|\s*Err:\s*([+-]?[\d.]+)")

BG, PANEL, BTN, TERM = "#14161a", "#1d2026", "#2a2e36", "#0d0f12"
FG, MUTED, ACCENT, GREEN, RED, ORANGE = "#e6e6e6", "#7d8590", "#4c8dff", "#3fb950", "#f85149", "#d29922"
FONT = "Helvetica"
STATS = ("Action", "Speed", "Battery", "Target", "Distance", "Score", "Laps", "Time left")


class BoatGUI:
    def __init__(self, root):
        self.root = root
        self.proc = None
        self.reader_thread = None
        self.mode = None
        self.partial = ""
        self.out = queue.Queue()

        root.title("DD-Boat 11")
        root.configure(bg=BG)
        root.geometry("1120x700")
        root.minsize(900, 600)

        # Header: name, status, big STOP
        top = tk.Frame(root, bg=BG)
        top.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(top, text="DD-BOAT 11", bg=BG, fg=FG, font=(FONT, 16, "bold")).pack(side="left")
        self.status = tk.Label(top, bg=BG, font=(FONT, 13, "bold"))
        self.status.pack(side="left", padx=16)
        tk.Label(top, text=BOAT, bg=BG, fg=MUTED, font=(FONT, 11)).pack(side="left")
        self.button(top, "STOP", lambda: self.switch(None), bg=RED, width=10).pack(side="right")

        body = tk.Frame(root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        left = tk.Frame(body, bg=PANEL, padx=16, pady=16)
        left.pack(side="left", fill="y")
        right = tk.Frame(body, bg=TERM)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        # Mode selector
        modes = tk.Frame(left, bg=PANEL)
        modes.pack(fill="x")
        self.mode_btns = {}
        for m, label in (("RC", "RC teleop"), ("AUTO", "Autonomous")):
            b = self.button(modes, label, lambda m=m: self.switch(m))
            b.pack(side="left", fill="x", expand=True, padx=(0, 6) if m == "RC" else 0)
            self.mode_btns[m] = b

        # Instruments: compass (AUTO heading / target) and motor bars (RC)
        inst = tk.Frame(left, bg=PANEL)
        inst.pack(pady=16)
        self.compass = tk.Canvas(inst, width=170, height=170, bg=PANEL, highlightthickness=0)
        self.compass.pack(side="left")
        self.motors = tk.Canvas(inst, width=100, height=170, bg=PANEL, highlightthickness=0)
        self.motors.pack(side="left", padx=(16, 0))

        # Stat tiles
        grid = tk.Frame(left, bg=PANEL)
        grid.pack(fill="x")
        self.stats = {}
        for i, name in enumerate(STATS):
            tile = tk.Frame(grid, bg=BTN, padx=10, pady=6)
            tile.grid(row=i // 2, column=i % 2, sticky="nsew", padx=3, pady=3)
            tk.Label(tile, text=name.upper(), bg=BTN, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
            self.stats[name] = tk.Label(tile, bg=BTN, fg=FG, font=(FONT, 13, "bold"), anchor="w", width=13)
            self.stats[name].pack(anchor="w")
        grid.columnconfigure((0, 1), weight=1)

        # On-screen D-pad and speed buttons (same keys as the keyboard)
        pad = tk.Frame(left, bg=PANEL)
        pad.pack(pady=(16, 6))
        self.pad = {}
        for key, label, r, c in (("w", "▲", 0, 1), ("a", "◀", 1, 0), (" ", "■", 1, 1), ("d", "▶", 1, 2), ("s", "▼", 2, 1)):
            b = self.button(pad, label, lambda k=key: self.rc_key(k), width=4)
            b.grid(row=r, column=c, padx=3, pady=3)
            self.pad[key] = b
        speeds = tk.Frame(left, bg=PANEL)
        speeds.pack()
        for key, label in (("1", "Slow"), ("2", "Med"), ("3", "Fast"), ("-", "−"), ("+", "+")):
            b = self.button(speeds, label, lambda k=key: self.rc_key(k), width=4)
            b.pack(side="left", padx=3)
            self.pad[key] = b
        tk.Label(left, text="Keyboard: WASD / arrows · Space = stop", bg=PANEL, fg=MUTED,
                 font=(FONT, 10)).pack(pady=(10, 0))

        # Terminal
        tk.Label(right, text="TERMINAL", bg=TERM, fg=MUTED, font=(FONT, 9), anchor="w").pack(fill="x", padx=12, pady=(8, 0))
        self.log = tk.Text(right, bg=TERM, fg="#c9d1d9", font="TkFixedFont", state="disabled", takefocus=0,
                           relief="flat", highlightthickness=0, padx=12, pady=8)
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("cmd", foreground=ACCENT)

        root.bind_all("<Key>", self.on_key)
        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.reset_ui()
        self.set_status("IDLE", MUTED)
        self.poll()

    # ── Widgets ────────────────────────────────────────────────────────────
    def button(self, parent, text, command, bg=BTN, width=None):
        # Labels instead of Buttons: colours work on macOS and they never take focus (Space must reach the boat)
        b = tk.Label(parent, text=text, bg=bg, fg=FG, font=(FONT, 12, "bold"), padx=12, pady=8,
                     width=width, cursor="hand2")
        b.base = bg
        b.bind("<Button-1>", lambda e: (self.flash(b), command()))
        return b

    def flash(self, b):
        b.config(bg=ACCENT)
        self.root.after(120, lambda: b.config(bg=b.base))

    def set_status(self, text, color):
        self.status.config(text="● " + text, fg=color)
        for m, b in self.mode_btns.items():
            b.base = ACCENT if m == self.mode else BTN
            b.config(bg=b.base)
        self.root.update_idletasks()

    def reset_ui(self):
        for label in self.stats.values():
            label.config(text="—")
        self.draw_compass()
        self.draw_motors()

    def draw_compass(self, hdg=None, err=None):
        c, cx, cy, r = self.compass, 85, 85, 72
        c.delete("all")

        def pt(deg, d):
            return cx + d * math.sin(math.radians(deg)), cy - d * math.cos(math.radians(deg))

        c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=BTN, width=3)
        for deg, txt in ((0, "N"), (90, "E"), (180, "S"), (270, "W")):
            c.create_text(*pt(deg, r - 14), text=txt, fill=MUTED, font=(FONT, 10, "bold"))
        if hdg is None:
            c.create_text(cx, cy, text="—", fill=MUTED, font=(FONT, 16))
            return
        if err is not None:
            c.create_line(cx, cy, *pt(hdg + err, r - 4), fill=GREEN, width=2, dash=(4, 3))
        c.create_line(cx, cy, *pt(hdg, r - 24), fill=ACCENT, width=4, arrow="last")
        c.create_text(cx, cy + 30, text="{:.0f}°".format(hdg), fill=FG, font=(FONT, 12, "bold"))

    def draw_motors(self, left=None, right=None):
        c, mid, half = self.motors, 75, 62
        c.delete("all")
        for x, name, val in ((14, "L", left), (58, "R", right)):
            c.create_rectangle(x, mid - half, x + 28, mid + half, fill=BTN, outline="")
            if val:
                y = mid - half * max(-1.0, min(1.0, val / 120.0))
                c.create_rectangle(x, min(y, mid), x + 28, max(y, mid), fill=GREEN if val > 0 else RED, outline="")
            c.create_line(x - 3, mid, x + 31, mid, fill=MUTED)
            c.create_text(x + 14, 156, text="{} {}".format(name, "—" if val is None else "{:+d}".format(val)),
                          fill=MUTED, font=(FONT, 10, "bold"))

    def append(self, text, tag=None):
        self.log.config(state="normal")
        self.log.insert("end", text, tag)
        self.log.delete("1.0", "end-1000l")  # keep the last 1000 lines
        self.log.see("end")
        self.log.config(state="disabled")

    # ── Boat control ───────────────────────────────────────────────────────
    def ssh_cmd(self, cmd):
        self.append("\n$ ssh {} '{}'\n".format(BOAT, cmd), "cmd")
        return "cd {} && {}".format(REMOTE_DIR, cmd)

    def switch(self, mode):
        self.set_status("Stopping…", ORANGE)
        p, self.proc = self.proc, None
        if p is not None and p.poll() is None:
            self.send(p, "\x03")  # Ctrl+C -> KeyboardInterrupt -> script's finally sends (0, 0)
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
        if self.reader_thread is not None:
            self.reader_thread.join(timeout=2)  # old script's last output goes to the terminal before stop.py's
            self.flush(parse=False)
        try:
            r = subprocess.run(SSH + [self.ssh_cmd("python3 stop.py")], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=15)
            self.append(r.stdout.decode("utf-8", "replace"))
        except subprocess.TimeoutExpired:
            self.append("[WARN] stop.py timed out - is the boat reachable?\n")

        self.mode = mode
        self.reset_ui()
        if mode is None:
            self.set_status("IDLE · motors stopped at " + time.strftime("%H:%M:%S"), MUTED)
            return
        # -tt gives the remote script a real terminal (rc_teleop needs termios, Ctrl+C becomes SIGINT)
        self.proc = subprocess.Popen(SSH[:1] + ["-tt"] + SSH[1:] + [self.ssh_cmd(MODES[mode])],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.reader_thread = threading.Thread(target=self.reader, args=(self.proc,), daemon=True)
        self.reader_thread.start()
        self.set_status("RC TELEOP" if mode == "RC" else "AUTONOMOUS", GREEN if mode == "RC" else ACCENT)

    def send(self, p, s):
        try:
            p.stdin.write(s.encode())
            p.stdin.flush()
        except OSError:
            pass

    def rc_key(self, k):
        if self.mode != "RC" or self.proc is None:
            return
        self.send(self.proc, k)
        if k.lower() in self.pad:
            self.flash(self.pad[k.lower()])

    def on_key(self, e):
        k = ARROWS.get(e.keysym, e.char)
        if k:
            self.rc_key("+" if k == "=" else k)
        return "break"

    def reader(self, p):
        for chunk in iter(lambda: p.stdout.read1(4096), b""):
            self.out.put(chunk.decode("utf-8", "replace"))
        self.out.put("\n[ssh exited, code {}]\n".format(p.wait()))

    def parse(self, line):
        """Update the panel from a status line. True if the line should stay out of the terminal."""
        m = RC_LINE.search(line)
        if m:
            label, spd, left, right, batt = m.groups()
            for name, val in (("Action", label.strip().title()), ("Speed", spd), ("Battery", batt)):
                self.stats[name].config(text=val)
            self.draw_motors(int(left), int(right))
            return True  # rc_teleop rewrites this line 50x/s, the panel already shows it
        m = AUTO_LINE.search(line)
        if m:
            rem, target, dist, score, laps, hdg, err = m.groups()
            for name, val in (("Action", "Racing"), ("Target", target), ("Distance", dist + " m"),
                              ("Score", score), ("Laps", laps), ("Time left", rem + " s")):
                self.stats[name].config(text=val)
            self.draw_compass(float(hdg), float(err))
        return False

    def flush(self, parse=True):
        text = self.partial
        while not self.out.empty():
            text += self.out.get_nowait()
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        self.partial = lines.pop()  # incomplete last line waits for the next chunk
        shown = [l for l in lines if not (parse and self.parse(l))]
        if shown:
            self.append("\n".join(shown) + "\n")

    def poll(self):
        self.flush()
        if self.proc is not None and self.proc.poll() is not None:
            self.proc, self.mode = None, None
            self.set_status("IDLE · script ended", MUTED)
        self.root.after(50, self.poll)

    def quit(self):
        self.switch(None)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    BoatGUI(root)
    root.mainloop()
