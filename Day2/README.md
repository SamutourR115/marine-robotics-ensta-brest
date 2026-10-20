# Localization of a robot group with interval contractors

This exercise localizes a group of 8 robots in the plane. The inputs are:

- the inter-robot distances (rounded to the nearest integer), and
- the approximate positions (±3 m) of 3 "anchor" robots.

The robots' positions are never computed as single points. Each coordinate is kept as an **interval** that is guaranteed to contain the true value. **Contractors** then shrink those intervals until they stop changing. The result is a box `[x] × [y]` per robot that is certain to contain it.

## Files

| File | Role |
|---|---|
| [myinterval.py](myinterval.py) | Minimal interval arithmetic library (`Interval` class, `sqr`, `sqrt`, `exp`, `log`, `&`, `|` …) |
| [mycontractor.py](mycontractor.py) | Elementary contractors built on top of it (`cadd`, `cminus`, `cmul`, `csqr`, `cexp`) |
| [loc_start.py](loc_start.py) | The localization problem: data, constraint propagation loop, plot |
| `roblib` (pip package) | Plotting helpers from the course (`init_figure`, `draw_box_border`, `pause`) |

## 1. Interval arithmetic ([myinterval.py](myinterval.py))

An `Interval(a, b)` is the set `[a, b]`. `oo = float('inf')`, so `Interval(-oo, oo)` means "completely unknown". If `a > b`, both bounds are set to `nan`, which is how the code represents the **empty set** (`is_empty()` checks for `nan`).

Each operation returns the smallest interval that contains every possible result:

| Operation | Rule |
|---|---|
| `x + y` | `[x.lb + y.lb, x.ub + y.ub]` |
| `x - y` | `[x.lb - y.ub, x.ub - y.lb]` |
| `x * y` | min/max of the 4 bound products |
| `x / y` | `x * [1/y.ub, 1/y.lb]`, or `[-oo, oo]` if `0 ∈ y` |
| `x & y` | intersection (empty if either side is empty) |
| `x \| y` | interval hull of the union |
| `sqr(x)` | `[0, max²]` if `0 ∈ x`, otherwise `[min², max²]` |
| `sqrt(x)` | `√` of `x ∩ [0, oo]` |

Run `python myinterval.py` for a small demo.

## 2. Contractors ([mycontractor.py](mycontractor.py))

A contractor for a constraint `f(x, y, z) = 0` takes the current domains and returns domains that are **equal or smaller**, and it never removes a value that could satisfy the constraint. It does this by applying the constraint in every direction and intersecting the result with what we already knew.

```python
def cadd(z, x, y):          # constraint z = x + y
    return z & x+y, x & z-y, y & z-x
```

Example (from `python mycontractor.py`): `a=[-5,3]`, `b=[4,10]`, `c=[12,100]` with `c = a + b`
→ `c=[12,13]`, `a=[2,3]`, `b=[9,10]`.

| Contractor | Constraint | Projections |
|---|---|---|
| `cadd(z,x,y)` | `z = x + y` | `z∩(x+y)`, `x∩(z−y)`, `y∩(z−x)` |
| `cminus(z,x,y)` | `z = x − y` | `z∩(x−y)`, `x∩(z+y)`, `y∩(x−z)` |
| `cmul(z,x,y)` | `z = x · y` | `z∩(x·y)`, `x∩(z/y)`, `y∩(z/x)` |
| `cexp(y,x)` | `y = eˣ` | `y∩exp(x)`, `x∩log(y)` |
| `csqr(y,x)` | `y = x²` | see below |

**`csqr` is the subtle one.** `x²` is not injective, so the inverse has two branches, `−√y` and `+√y`. The function:

1. splits `x` into `x⁻ = x ∩ [−oo, 0]` and `x⁺ = x ∩ [0, oo]`,
2. contracts `y` against `sqr(x⁻) ∪ sqr(x⁺)`,
3. contracts each half separately (`x⁻ ∩ −√y`, `x⁺ ∩ √y`) and returns their hull.

If `y` becomes empty, both outputs are empty, which means the constraint is inconsistent.

## 3. The localization problem ([loc_start.py](loc_start.py))

### Data

```python
_x = [66, -44, -9, -30, 12, -20, 0, -50]   # true positions (used only to
_y = [-70, 55, 30, -15, 70,  0, 10, -50]   # simulate measurements and to plot)
```

- **Distances:** `_d[i][j] = round(‖p_j − p_i‖)`. Since rounding loses at most 0.5, the measurement domain is `D[i][j] = [d − 0.5, d + 0.5]`, and `D[i][i] = [0, 0]`.
- **Anchors:** robots 0, 1, 2 start with `X[i] = [x_i − 3, x_i + 3]` and `Y[i] = [y_i − 3, y_i + 3]` (drawn in blue).
- **Unknown robots:** robots 3 to 7 start at `[-oo, oo] × [-oo, oo]`.

### Decomposing the distance constraint

Every pair `(i, j)` gives the constraint

```
(x_j − x_i)² + (y_j − y_i)² = d_ij²
```

The constraint is broken into primitive operations, using intermediate variables that start at `[-oo, oo]`:

```
a  = x_j − x_i        b  = y_j − y_i
a2 = a²               b2 = b²
d2 = d_ij²            d2 = a2 + b2
```

### Forward–backward propagation

For each pair, the elementary contractors run **forward** (inputs → `d2`) and then **backward** (`d2` → inputs):

```python
# forward
a, X[j], X[i] = cminus(a, X[j], X[i])     # a  = xj - xi
b, Y[j], Y[i] = cminus(b, Y[j], Y[i])     # b  = yj - yi
a2, a         = csqr(a2, a)               # a2 = a²
b2, b         = csqr(b2, b)               # b2 = b²
d2, D[i][j]   = csqr(d2, D[i][j])         # d2 = d²
d2, a2, b2    = cadd(d2, a2, b2)          # d2 = a2 + b2   ← the actual constraint
# backward: same contractors in reverse order
a2, a         = csqr(a2, a)
b2, b         = csqr(b2, b)
a, X[j], X[i] = cminus(a, X[j], X[i])
b, Y[j], Y[i] = cminus(b, Y[j], Y[i])
```

The forward pass narrows the intermediate variables. The backward pass carries that information back to `X` and `Y`. The intermediate variables are reset to `[-oo, oo]` for each pair, because they are only scratch space for that one constraint.

### Fixed-point loop

The outer `for k in range(10)` loop applies all `N·(N−1)` pair contractors 10 times. One pass is not enough: once robot 3 is localized using the anchors, it can in turn help localize robot 7, and so on. Information spreads through the network over successive passes. Ten passes is a fixed budget. With this data the boxes stop changing after about 5 passes (the total box width goes 221 → 203 → 202.3 → 202.2 and then stays there).

### Output

The script prints `_d`, `X` and `Y`. It then draws each robot's true position (red square) over the anchor boxes (blue) and pauses for 10 s.

Box sizes obtained (width of `X`, `Y` in m):

| Robot | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| width X | 6 | 6 | 6 | 18.3 | 12.3 | 27.1 | 28.4 | 9.5 |
| width Y | 6 | 6 | 6 | 12.5 | 14.3 | 16.4 | 19.7 | 7.9 |

Every true position lies inside its box. That is the guarantee interval methods give: the result is **never wrong**, only more or less pessimistic.

## Running

```bash
python -m venv .venv && source .venv/bin/activate
pip install roblib          # pulls numpy, scipy, matplotlib
python loc_start.py
```

## Known limitations / gotchas

- **Name shadowing:** `from roblib import *` comes after `from mycontractor import *`, so in `loc_start.py` the name `sqrt` is **numpy's** `sqrt`, not the interval one. That is fine because it is only used on plain numbers there (to build `_d`). Inside `mycontractor.py`, `csqr` still uses the interval `sqrt`. Calling `sqrt(Interval(...))` in `loc_start.py` would not work. `sum` is also numpy's version, and numpy refuses to sum a generator.
- **Pessimism:** the boxes for robots 5 and 6 are wide because each constraint is contracted on its own. The intersection of several rings (annuli) is not convex, and its box hull is larger than the region the robot can actually be in. Bisection (SIVIA-style paving) would give a tighter description.
- **No convergence test:** the loop always runs 10 times. Stopping when no interval changes by more than ε would be more efficient.
- **Empty set:** if the data were inconsistent (e.g. anchor boxes too small), some intervals would become `[nan, nan]` and the propagation would spread emptiness everywhere. Nothing in the code checks for this.
