<div align="center">

# ROBOTson Crusoe: Let's Explore the Lost City

**BEST Fall Course 2026 · Marine Robotics · ENSTA Brest**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Field](https://img.shields.io/badge/Field-Marine%20Robotics-0A7EA4)
![Credits](https://img.shields.io/badge/ECTS-1.0-6C757D)
![Status](https://img.shields.io/badge/Status-In%20progress-F0AD4E)

*Notes, code and experiments from a one-week intensive course on autonomous marine robotics, from theory to field trials at Lake Guerlédan.*

</div>

---

## Table of Contents

- [About](#about)
- [Course Information](#course-information)
- [Curriculum](#curriculum)
- [Weekly Schedule](#weekly-schedule)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Progress](#progress)
- [References](#references)
- [Acknowledgments](#acknowledgments)
- [Disclaimer](#disclaimer)
- [Author](#author)

---

## About

This repository documents my work during **ROBOTson Crusoe**, a BEST (Board of European Students of Technology) course hosted at **ENSTA Brest**, France.

The course covers three key areas of marine robotics:

- **Autonomous robotic missions**: planning and executing missions without human intervention
- **Command and control**: modelling, heading control and guaranteed methods
- **Sensors**: acoustic, magnetic and optical perception in the marine environment

The course moves **from theory to practice on real systems**. Lectures and Python coding sessions are followed by a field lab and the piloting of real marine robots at **Lake Guerlédan**. The week ends with a **final lake challenge**.

### Learning objectives

By the end of the course, I aim to be able to:

1. Model a surface vessel and design a heading controller for it
2. Apply **interval analysis** to guaranteed localization
3. Reason about the **reachable sets** of a dynamical system
4. Train and evaluate a **reinforcement learning** agent for boat control
5. Build and use a basic **digital twin** of a marine robot
6. Remotely operate a marine craft in real conditions

---

## Course Information

| | |
|---|---|
| **Title** | ROBOTson Crusoe: Let's Explore the Lost City |
| **Organizers** | BEST, with ENSTA Brest |
| **Location** | ENSTA Brest and Lake Guerlédan, Brittany, France |
| **Period** | Fall 2026 (one week) |
| **Fields** | Computer Science · Automatic Control · Systems Engineering · Mechatronics |
| **Format** | Lectures · hands-on Python · robot piloting · field lab · final lake challenge |
| **Prerequisites** | Basic Python |
| **Assessment** | Project |
| **Credits** | 1 ECTS |

---

## Curriculum

| # | Module | Instructor | Folder |
|---|---|---|---|
| 1 | Introduction to Mobile Marine Robotics | Luc Jaulin | [`01-monday/01-intro-marine-robotics`](01-monday/01-intro-marine-robotics) |
| 2 | Autonomous Boats | Luc Jaulin | [`01-monday/02-autonomous-boats`](01-monday/02-autonomous-boats) |
| 3 | Heading Control of the Virtual DD-Boat | Antoine Morvan | [`01-monday/03-ddboat-heading-control`](01-monday/03-ddboat-heading-control) |
| 4 | Interval Analysis for Localization | Luc Jaulin | [`02-tuesday/01-interval-analysis`](02-tuesday/01-interval-analysis) |
| 5 | Reachability | Maël Godard | [`02-tuesday/02-reachability`](02-tuesday/02-reachability) |
| 6 | Robot Showcase | AICE | [`02-tuesday/03-aice-robots`](02-tuesday/03-aice-robots) |
| 7 | Reinforcement Learning for Autonomous Boats (Part 1) | Romain Bornier | [`03-wednesday/01-rl-part1`](03-wednesday/01-rl-part1) |
| 8 | Reinforcement Learning for Autonomous Boats (Part 2) | Romain Bornier | [`03-wednesday/02-rl-part2`](03-wednesday/02-rl-part2) |
| 9 | Digital Twins: Fundamentals | Antoine Morvan | [`04-thursday/01-digital-twins-basic`](04-thursday/01-digital-twins-basic) |
| 10 | Oceanic Robotics | Jean-Philippe Brunet | [`04-thursday/02-oceanic-robotics`](04-thursday/02-oceanic-robotics) |
| 11 | Digital Twins: Practice | Antoine Morvan | [`04-thursday/03-digital-twins-practice`](04-thursday/03-digital-twins-practice) |
| 12 | **The Race**: Final Challenge | Luc Jaulin | [`05-friday/the-race`](05-friday/the-race) |

<details>
<summary><b>Key questions addressed by each module</b></summary>

<br>

**Marine robotics and autonomous boats**
- What makes the marine environment harder for a robot than a ground environment?
- How is a surface vessel described as a state-space system **ẋ = f(x, u)**?
- What is the difference between point tracking and line following?

**Heading control (DD-Boat)**
- How is a desired heading turned into differential thrust commands?
- How should an angular error be computed so that it stays consistent across ±π?

**Interval analysis and reachability**
- What does it mean for a localization method to be *guaranteed*?
- How do contractors and bisection (e.g. SIVIA) characterize a solution set?
- Why is over-approximation the right choice for proving safety?

**Reinforcement learning**
- How is boat control formulated as a Markov decision process?
- How does the reward design shape, and sometimes distort, the learned behaviour?
- How can the sim-to-real gap be reduced?

**Digital twins and oceanic robotics**
- What separates a digital twin from a plain simulation?
- Why is energy the central constraint of long-duration ocean missions?
- How do submerged robots localize and communicate?

</details>

---

## Weekly Schedule

| Day | Time | Session | Instructor |
|---|---|---|---|
| **Mon** | 11:30–12:15 | Introduction to Mobile Marine Robotics | Luc Jaulin |
| | 14:30–16:00 | Autonomous Boats | Luc Jaulin |
| | 16:00–17:00 | Heading Control of the Virtual DD-Boat | Antoine Morvan |
| **Tue** | 10:00–12:00 | Interval Analysis for Localization | Luc Jaulin |
| | 14:00–15:30 | Reachability | Maël Godard |
| | 16:00–16:30 | Robot Showcase | AICE |
| **Wed** | 09:00–10:00 | Reinforcement Learning for Autonomous Boats (Part 1) | Romain Bornier |
| | 14:00–16:00 | Reinforcement Learning for Autonomous Boats (Part 2) | Romain Bornier |
| **Thu** | 09:00–11:00 | Digital Twins: Fundamentals | Antoine Morvan |
| | 11:00–12:00 | Oceanic Robotics | Jean-Philippe Brunet |
| | 13:00–15:00 | Digital Twins: Practice | Antoine Morvan |
| **Fri** | 09:00–12:00 | The Race: Final Challenge | Luc Jaulin |

---

## Repository Structure

```
.
├── README.md
├── requirements.txt
├── 01-monday/
│   ├── 01-intro-marine-robotics/
│   ├── 02-autonomous-boats/
│   └── 03-ddboat-heading-control/
├── 02-tuesday/
│   ├── 01-interval-analysis/
│   ├── 02-reachability/
│   └── 03-aice-robots/
├── 03-wednesday/
│   ├── 01-rl-part1/
│   └── 02-rl-part2/
├── 04-thursday/
│   ├── 01-digital-twins-basic/
│   ├── 02-oceanic-robotics/
│   └── 03-digital-twins-practice/
├── 05-friday/
│   └── the-race/
└── assets/                 # figures, photos and videos
```

Each module folder follows the same layout:

| Path | Content |
|---|---|
| `README.md` | Summary of the module, key concepts and takeaways |
| `src/` | Source code |
| `results/` | Plots, logs and videos |

---

## Getting Started

### Requirements

- Python 3.x
- NumPy, Matplotlib
- [Codac](https://codac.io) (interval analysis and constraint programming)

### Installation

```bash
git clone https://github.com/<username>/<repository>.git
cd <repository>
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Usage

Each module can be run independently. See the `README.md` inside each folder for module-specific instructions.

---

## Progress

| Module | Notes | Code | Status |
|---|:---:|:---:|:---:|
| Introduction to Mobile Marine Robotics | ☐ | n/a | Pending |
| Autonomous Boats | ☐ | ☐ | Pending |
| Heading Control of the Virtual DD-Boat | ☐ | ☐ | Pending |
| Interval Analysis for Localization | ☐ | ☐ | Pending |
| Reachability | ☐ | ☐ | Pending |
| Robot Showcase (AICE) | ☐ | n/a | Pending |
| Reinforcement Learning (Part 1) | ☐ | ☐ | Pending |
| Reinforcement Learning (Part 2) | ☐ | ☐ | Pending |
| Digital Twins: Fundamentals | ☐ | ☐ | Pending |
| Oceanic Robotics | ☐ | n/a | Pending |
| Digital Twins: Practice | ☐ | ☐ | Pending |
| The Race: Final Challenge | ☐ | ☐ | Pending |

---

## References

- L. Jaulin, *Mobile Robotics*, ISTE / Wiley.
- L. Jaulin, M. Kieffer, O. Didrit, É. Walter, *Applied Interval Analysis*, Springer, 2001.
- L. Jaulin, teaching resources: <https://www.ensta-bretagne.fr/jaulin/>
- Codac library: <https://codac.io>

---

## Acknowledgments

I thank the instructors, **Luc Jaulin**, **Antoine Morvan**, **Maël Godard**, **Romain Bornier** and **Jean-Philippe Brunet**, for their teaching, the **AICE** team for presenting their robots, and **BEST** and **ENSTA Brest** for organizing this course.

---

## Disclaimer

This repository contains my personal notes and implementations. Course materials (slides, handouts and starter code) remain the property of their respective authors and are not redistributed here. Any errors are my own.

---

## Author

**Sam**, BSc student in Computer Science (Intelligent Systems), University of Liège
[GitHub](https://github.com/<username>) · [LinkedIn](https://www.linkedin.com/in/<profile>)
