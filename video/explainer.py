"""
Explainer video for the Ph.D. dissertation
"Quantum Computing and Circuit Simulation" -- Ziqing Guo, Texas Tech University, 2026.

3Blue1Brown-style: dark background, one idea at a time, captions instead of narration.
Manim Community (no LaTeX: Text / MarkupText only, Unicode math).

Render everything and concatenate:

    python explainer.py --quality m            # 1280x720 @ 30 fps
    python explainer.py --quality h            # 1920x1080 @ 30 fps
    python explainer.py --quality m --only S02_MemoryWall S03_QGear

Media (per-scene renders) go to --media_dir (default: a _media folder next to this
file), the final file to --out (default: thesis_explainer.mp4 next to this file).
"""
from __future__ import annotations

import numpy as np
from manim import *

# ----------------------------------------------------------------- palette
BG = "#0b0f19"
INK = "#e8e8e8"
WHITE = "#ffffff"
SCARLET = "#CC0000"       # Texas Tech scarlet: emphasis only
MUTED = "#8a93a3"         # axes, secondary labels
GRID = "#242b3a"          # faint gridlines
C_SCALE = "#4C78A8"
C_DATA = "#F58518"
C_NOISE = "#54A24B"
C_SYNTH = "#B279A2"
C_TRUST = "#9D9D9D"
FONT = "Avenir Next"
MONO = "Menlo"

LAYERS = [
    dict(name="Scale", color=C_SCALE, rq="RQ1", ch="Chapter III",
         what="simulation"),
    dict(name="Data", color=C_DATA, rq="RQ2", ch="Chapter IV",
         what="vectorized encodings for quantum learning"),
    dict(name="Noise", color=C_NOISE, rq="RQ3", ch="Chapter V",
         what="hardware-aware optimization on noisy devices"),
    dict(name="Synthesis", color=C_SYNTH, rq="RQ4", ch="Chapter VI",
         what="learned circuit synthesis toward fault-tolerant budgets"),
    dict(name="Trust", color=C_TRUST, rq="RQ5", ch="Chapters VII–VIII",
         what="security-aware error correction and post-quantum cryptography"),
]
SECTOR_DEG = 66
CAPTION_MAX_WIDTH = 12.6


# ----------------------------------------------------------------- helpers
def T(s, size=32, color=INK, weight="NORMAL", **kw):
    kw.setdefault("font", FONT)
    return Text(s, font_size=size, color=color, weight=weight, **kw)


def counter(tracker, fmt, size=32, color=INK, weight="NORMAL", anchor=None, edge=ORIGIN):
    """Text that re-renders from a ValueTracker (DecimalNumber would need LaTeX)."""
    def build():
        t = T(fmt(tracker.get_value()), size, color, weight)
        if anchor is not None:
            t.move_to(anchor, aligned_edge=edge)
        return t
    return always_redraw(build)


def vbar(tracker, x, y0, width, unit, color, opacity=0.95):
    """Vertical bar, height = tracker * unit, bottom-centre at (x, y0)."""
    def build():
        h = max(tracker.get_value() * unit, 0.002)
        return (Rectangle(width=width, height=h).set_fill(color, opacity)
                .set_stroke(width=0).move_to([x, y0, 0], aligned_edge=DOWN))
    return always_redraw(build)


def hbar(tracker, x0, y, height, unit, color, opacity=0.95):
    """Horizontal bar, width = tracker * unit, left-centre at (x0, y)."""
    def build():
        w = max(tracker.get_value() * unit, 0.002)
        return (Rectangle(width=w, height=height).set_fill(color, opacity)
                .set_stroke(width=0).move_to([x0, y, 0], aligned_edge=LEFT))
    return always_redraw(build)


def axis(start, end):
    return Line(start, end, color=MUTED, stroke_width=2)


def box(label, w=None, h=0.55, color=INK, size=18, fill=BG, fill_opacity=1.0, stroke=2,
        radius=0.12, text_color=INK, font=None, pad=0.45):
    """Rounded box around a label; width defaults to the label width plus padding."""
    kw = {"font": font} if font else {}
    t = T(label, size, text_color, **kw)
    if w is None:
        w = t.width + pad
    r = RoundedRectangle(corner_radius=radius, width=w, height=h)
    r.set_fill(fill, fill_opacity).set_stroke(color, stroke)
    t.move_to(r)
    g = VGroup(r, t)
    g.rect, g.label = r, t
    return g


def arrow(a, b, color=MUTED, sw=3, tip=0.2):
    return Arrow(a, b, buff=0, color=color, stroke_width=sw, tip_length=tip,
                 max_tip_length_to_length_ratio=0.5, max_stroke_width_to_length_ratio=20)


def edge_point(mob, d, gap=0.1):
    """Point on the ray from mob's centre along d, just outside its bounding box."""
    hw, hh = mob.width / 2, mob.height / 2
    t = min(hw / abs(d[0]) if abs(d[0]) > 1e-6 else 1e9,
            hh / abs(d[1]) if abs(d[1]) > 1e-6 else 1e9)
    return mob.get_center() + d * (t + gap)


class StackMap(VGroup):
    """The recurring map: QPU in the centre, five layer sectors around it."""

    def __init__(self, active=None, labels=True, qpu_text=True,
                 r_in=1.25, r_out=1.85, dim=0.18, **kw):
        super().__init__(**kw)
        self.r_out = r_out
        self.qpu_circle = Circle(radius=0.8, color=INK, stroke_width=3,
                                 fill_color=BG, fill_opacity=1)
        self.qpu_text = T("QPU", 34, WHITE, "SEMIBOLD") if qpu_text else VGroup()
        self.sectors, self.labels, self.dirs = VGroup(), VGroup(), []
        for i, L in enumerate(LAYERS):
            mid = 90 - 72 * i
            d = np.array([np.cos(mid * DEGREES), np.sin(mid * DEGREES), 0.0])
            self.dirs.append(d)
            on = active is None or active == i
            sec = AnnularSector(inner_radius=r_in, outer_radius=r_out,
                                angle=SECTOR_DEG * DEGREES,
                                start_angle=(mid - SECTOR_DEG / 2) * DEGREES,
                                color=L["color"], fill_opacity=0.92 if on else dim,
                                stroke_width=0)
            self.sectors.add(sec)
            if labels:
                name = T(L["name"], 32, L["color"] if on else MUTED, "SEMIBOLD")
                sub = T(f'{L["rq"]} · {L["ch"]}', 20, INK if on else MUTED)
                lab = VGroup(name, sub).arrange(DOWN, buff=0.08)
                lab.next_to(d * r_out, d, buff=0.22)
                self.labels.add(lab)
        self.add(self.sectors, self.qpu_circle, self.qpu_text, self.labels)


class Base(Scene):
    def setup(self):
        self.camera.background_color = BG
        self._caption = None

    # -- captions at the bottom of the frame
    def caption(self, s, size=30, rt=0.7, color=INK, **kw):
        new = T(s, size, color, **kw)
        if new.width > CAPTION_MAX_WIDTH:
            new.scale_to_fit_width(CAPTION_MAX_WIDTH)
        new.to_edge(DOWN, buff=0.45)
        anims = [FadeIn(new, shift=UP * 0.15)]
        if self._caption is not None:
            anims.append(FadeOut(self._caption, shift=UP * 0.15))
        self.play(*anims, run_time=rt)
        self._caption = new
        return new

    def clear_caption(self, rt=0.5):
        if self._caption is not None:
            self.play(FadeOut(self._caption), run_time=rt)
            self._caption = None

    def heading(self, s, color=WHITE, size=40):
        h = T(s, size, color, "SEMIBOLD").to_edge(UP, buff=0.4)
        self.play(FadeIn(h, shift=DOWN * 0.2), run_time=0.7)
        return h

    def fade_all(self, rt=0.6):
        mobs = list(self.mobjects)
        for m in mobs:
            m.clear_updaters()
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=rt)
        self._caption = None

    # -- recurring map
    def small_map(self, idx):
        return (StackMap(active=idx, labels=False, qpu_text=False)
                .scale(0.23).to_corner(UL, buff=0.3))

    def layer_header(self, idx, small):
        L = LAYERS[idx]
        name = T(L["name"], 40, L["color"], "SEMIBOLD")
        sub = T(f'{L["rq"]} · {L["ch"]}', 22, MUTED)
        hdr = VGroup(name, sub).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
        hdr.next_to(small, RIGHT, buff=0.35)
        return hdr

    def layer_intro(self, idx):
        """Full map with the active layer highlighted, then shrink it to the corner."""
        L = LAYERS[idx]
        full = StackMap(active=idx).scale(0.9).shift(DOWN * 0.1)
        self.play(FadeIn(full), run_time=0.7)
        self.play(Indicate(full.sectors[idx], scale_factor=1.1, color=L["color"]), run_time=0.9)
        self.wait(0.5)
        small = self.small_map(idx)
        hdr = self.layer_header(idx, small)
        self.play(FadeOut(full.labels), FadeOut(full.qpu_text),
                  Transform(full.sectors, small.sectors),
                  Transform(full.qpu_circle, small.qpu_circle), run_time=0.9)
        self.play(FadeIn(hdr, shift=RIGHT * 0.2), run_time=0.5)
        return hdr


# ================================================================= 1. title
class S01_Title(Base):
    def construct(self):
        ring = StackMap(labels=False, qpu_text=False).scale(1.7)
        ring.sectors.set_fill(opacity=0.10)
        ring.qpu_circle.set_stroke(opacity=0.15).set_fill(opacity=0)
        ring.add_updater(lambda m, dt: m.rotate(0.04 * dt))
        self.add(ring)

        over = T("Ph.D. Dissertation · Computer Science", 22, MUTED).shift(UP * 2.1)
        title = T("Quantum Computing\nand Circuit Simulation", 56, WHITE, "SEMIBOLD",
                  line_spacing=0.9).shift(UP * 0.6)
        rule = Line(LEFT * 2.2, RIGHT * 2.2, color=SCARLET, stroke_width=4).next_to(title, DOWN, buff=0.45)
        author = T("Ziqing Guo", 36, INK, "MEDIUM").next_to(rule, DOWN, buff=0.4)
        uni = T("Texas Tech University · 2026", 26, MUTED).next_to(author, DOWN, buff=0.22)

        self.play(FadeIn(over), run_time=0.8)
        self.play(Write(title), run_time=2.2)
        self.play(GrowFromCenter(rule), run_time=0.7)
        self.play(LaggedStart(FadeIn(author, shift=UP * 0.2), FadeIn(uni, shift=UP * 0.2),
                              lag_ratio=0.3), run_time=1.0)
        self.wait(3.0)
        self.fade_all(0.8)


# ================================================================= 2. memory wall
class S02_MemoryWall(Base):
    def construct(self):
        self.heading("Exact state-vector simulation")
        self.caption("n qubits  →  2ⁿ amplitudes × 16 bytes")
        self.wait(1.0)

        X0, Y0, XR = -4.3, -2.0, 3.1   # axis origin and right end
        DEC = 0.68                      # scene units per decade
        XS = [-3.3 + 1.4 * i for i in range(5)]
        qubits = [26, 30, 34, 38, 42]
        gb = [1.1, 17, 275, 4400, 70000]
        vlabels = ["1.1 GB", "17 GB", "275 GB", "4.4 TB", "70 TB"]

        def y_of(v):                    # baseline = 100 MB, six decades
            return Y0 + (np.log10(v) + 1) * DEC

        top = Y0 + 6 * DEC
        yaxis = axis([X0, Y0, 0], [X0, top + 0.1, 0])
        xaxis = axis([X0, Y0, 0], [XR, Y0, 0])
        grid, ticks = VGroup(), VGroup()
        for k, name in enumerate(["1 GB", "10 GB", "100 GB", "1 TB", "10 TB", "100 TB"], start=1):
            y = Y0 + k * DEC
            grid.add(Line([X0, y, 0], [XR, y, 0], color=GRID, stroke_width=1))
            ticks.add(T(name, 18, MUTED).next_to([X0, y, 0], LEFT, buff=0.15))
        ylab = T("memory (log scale)", 20, MUTED).next_to([X0, top + 0.1, 0], UP, buff=0.15)
        xlab = T("qubits", 20, MUTED).move_to([(X0 + XR) / 2, Y0 - 0.8, 0])

        bars, vals, xt = VGroup(), VGroup(), VGroup()
        for x, q, v, lab in zip(XS, qubits, gb, vlabels):
            bar = (Rectangle(width=1.0, height=y_of(v) - Y0).set_fill(C_SCALE, 0.95)
                   .set_stroke(width=0).move_to([x, Y0, 0], aligned_edge=DOWN))
            bars.add(bar)
            vals.add(T(lab, 18, WHITE, "MEDIUM").move_to(bar.get_top() + DOWN * 0.24))
            xt.add(T(str(q), 20, INK).next_to([x, Y0, 0], DOWN, buff=0.18))

        self.play(Create(xaxis), Create(yaxis), FadeIn(grid), FadeIn(ticks),
                  FadeIn(ylab), FadeIn(xlab), run_time=1.0)
        for bar, val, t in zip(bars, vals, xt):
            self.play(GrowFromEdge(bar, DOWN), FadeIn(t), run_time=0.6)
            self.play(FadeIn(val), run_time=0.25)
        self.wait(0.5)
        self.caption("Every qubit doubles the memory.", t2c={"doubles": SCARLET})
        self.wait(2.2)

        for v, name in [(40, "1 A100 · 40 GB"), (512, "CPU node · 512 GB")]:
            y = y_of(v)
            ln = DashedLine([X0, y, 0], [XR, y, 0], color=INK, stroke_width=2, dash_length=0.12)
            lb = T(name, 19, INK).next_to([XR, y, 0], RIGHT, buff=0.15)
            self.play(Create(ln), FadeIn(lb), run_time=0.9)
            self.wait(0.4)
        self.wait(0.6)
        self.caption("Past 34 qubits, no single node holds the state.")
        self.wait(3.2)
        self.fade_all()


# ================================================================= 3. Q-GEAR
def circuit_glyph(color=C_SCALE):
    g = VGroup()
    ys = [0.55, 0.0, -0.55]
    wires = VGroup(*[Line([0, y, 0], [2.7, y, 0], color=MUTED, stroke_width=2) for y in ys])
    g.add(wires)

    def gate(label, x, y):
        b = Square(0.42).set_fill(BG, 1).set_stroke(color, 2.5).move_to([x, y, 0])
        return VGroup(b, T(label, 16, INK).move_to(b))

    cx = VGroup(Line([1.15, ys[0], 0], [1.15, ys[1], 0], color=color, stroke_width=2.5),
                Dot([1.15, ys[0], 0], radius=0.07, color=color),
                Circle(radius=0.14, color=color, stroke_width=2.5).move_to([1.15, ys[1], 0]),
                Line([1.15, ys[1] + 0.14, 0], [1.15, ys[1] - 0.14, 0], color=color, stroke_width=2.5),
                Line([1.01, ys[1], 0], [1.29, ys[1], 0], color=color, stroke_width=2.5))
    gates = VGroup(gate("H", 0.5, ys[0]), cx, gate("Rz", 0.8, ys[2]),
                   gate("X", 1.85, ys[1]), gate("Ry", 2.15, ys[2]))
    g.add(gates)
    g.gates = gates
    return g


def gpu_grid(k, size=2.8, color=C_SCALE):
    side = size / k
    sq = [Square(side * 0.86).set_fill(color, 0.9).set_stroke(width=0) for _ in range(k * k)]
    return VGroup(*sq).arrange_in_grid(rows=k, cols=k, buff=side * 0.14)


class S03_QGear(Base):
    def construct(self):
        name = T("Q-GEAR", 44, C_SCALE, "SEMIBOLD")
        sub = T("Scale · RQ1 · Chapter III", 22, MUTED)
        hdr = VGroup(name, sub).arrange(RIGHT, buff=0.35, aligned_edge=DOWN).to_corner(UL, buff=0.4)
        self.play(FadeIn(hdr, shift=RIGHT * 0.2), run_time=0.7)
        self.caption("A Qiskit circuit, converted gate by gate.")

        # circuit -> tensors
        circ = circuit_glyph().scale(1.15).move_to([-4.9, 0.5, 0])
        clab = T("Qiskit circuit", 22, INK).next_to(circ, DOWN, buff=0.35)
        self.play(Create(circ[0]), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(g, scale=0.6) for g in circ.gates], lag_ratio=0.2), FadeIn(clab),
                  run_time=1.0)
        self.wait(0.6)

        blocks = VGroup(*[box(n, 2.5, 0.6, C_SCALE, size=20, fill=C_SCALE, fill_opacity=0.22, font=MONO)
                          for n in ["circ_type", "gate_type", "gate_param"]])
        blocks.arrange(DOWN, buff=0.2).move_to([-0.9, 0.5, 0])
        blab = T("three tensors", 22, INK).next_to(blocks, DOWN, buff=0.35)
        a1 = arrow(circ.get_right() + RIGHT * 0.15, blocks.get_left() + LEFT * 0.15, C_SCALE)
        self.play(GrowArrow(a1), run_time=0.5)
        self.play(FadeIn(blocks, shift=RIGHT * 0.2), FadeIn(blab), run_time=0.7)

        flows = []
        for i, g in enumerate(circ.gates):
            cp = g.copy()
            tgt = (Square(0.14).set_fill(C_SCALE, 1).set_stroke(width=0)
                   .move_to(blocks[i % 3].get_left() + RIGHT * 0.3))
            flows.append(Succession(Transform(cp, tgt), FadeOut(cp)))
        self.play(LaggedStart(*flows, lag_ratio=0.25), run_time=2.4)
        self.wait(0.4)

        # tensors -> CUDA-Q kernels -> GPUs
        gpos = np.array([4.5, 0.5, 0])
        a2 = arrow(blocks.get_right() + RIGHT * 0.15, gpos + LEFT * 1.6, C_SCALE)
        klab = T("CUDA-Q kernels", 18, INK).next_to(a2, UP, buff=0.1)
        slab = T("containers · Slurm", 18, MUTED).next_to(a2, DOWN, buff=0.1)
        self.play(GrowArrow(a2), FadeIn(klab), FadeIn(slab), run_time=0.7)

        count = ValueTracker(1)
        grid = gpu_grid(1).move_to(gpos)
        cnt = counter(count, lambda v: f"{int(round(v)):,} A100 GPUs", 24, INK,
                      anchor=gpos + DOWN * 1.85)
        self.play(FadeIn(grid), FadeIn(cnt), run_time=0.5)
        self.caption("Up to 42 qubits on 1,024 GPUs of Perlmutter.")
        for k in [2, 4, 8, 16, 32]:
            new = gpu_grid(k).move_to(gpos)
            self.play(FadeTransform(grid, new), count.animate.set_value(k * k), run_time=0.6)
            grid = new
        self.wait(2.4)

        # wall-time comparison
        keep = {hdr, self._caption}
        gone = [m for m in self.mobjects if m not in keep]
        for m in gone:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in gone], run_time=0.6)

        ctitle = T("34-qubit circuit", 28, INK, "MEDIUM").move_to([0.6, 2.1, 0])
        XA, XB, YA = -2.6, 4.3, -1.3
        DECX = (XB - XA) / 5

        def x_of(sec):
            return XA + np.log10(sec) * DECX

        xaxis = axis([XA, YA, 0], [XB + 0.2, YA, 0])
        ticks = VGroup()
        for sec, name in [(1, "1 s"), (60, "1 min"), (3600, "1 h"), (86400, "1 day")]:
            x = x_of(sec)
            ticks.add(Line([x, YA, 0], [x, YA - 0.12, 0], color=MUTED, stroke_width=2),
                      T(name, 18, MUTED).next_to([x, YA - 0.12, 0], DOWN, buff=0.1))
        xlab = T("wall time (log scale)", 20, MUTED).move_to([(XA + XB) / 2, YA - 1.0, 0])
        self.play(FadeIn(ctitle), Create(xaxis), FadeIn(ticks), FadeIn(xlab), run_time=0.8)

        rows = [("128-core CPU node", 86400, "≈ 1 day", 0.45, 1.0),
                ("4 GPUs", 60, "≈ 1 minute", 0.95, -0.3)]
        for name, sec, val, op, y in rows:
            lab = T(name, 26, INK).next_to([XA - 0.3, y, 0], LEFT, buff=0)
            bar = (Rectangle(width=x_of(sec) - XA, height=0.7).set_fill(C_SCALE, op)
                   .set_stroke(width=0).move_to([XA, y, 0], aligned_edge=LEFT))
            v = T(val, 26, INK, "MEDIUM").next_to(bar, RIGHT, buff=0.15)
            self.play(FadeIn(lab), run_time=0.4)
            self.play(GrowFromEdge(bar, LEFT), run_time=1.0)
            self.play(FadeIn(v), run_time=0.3)
            self.wait(0.3)
        self.caption("One day on CPUs becomes one minute on four GPUs.")
        self.wait(3.2)
        self.fade_all()


# ================================================================= 4. the stack
class S04_Stack(Base):
    def construct(self):
        self.heading("A co-designed stack")
        m = StackMap().shift(DOWN * 0.15)
        self.play(GrowFromCenter(m.qpu_circle), FadeIn(m.qpu_text), run_time=0.8)
        self.caption("The QPU sits at the centre.")
        self.wait(1.2)
        for i, L in enumerate(LAYERS):
            d = m.dirs[i]
            self.play(FadeIn(m.sectors[i], shift=-d * 0.7), FadeIn(m.labels[i], shift=-d * 0.35),
                      run_time=0.8)
            self.caption(f'{L["name"]}  ·  {L["what"]}', rt=0.5, t2c={L["name"]: L["color"]})
            self.wait(1.7)
        self.wait(0.3)
        self.caption("Classical HPC surrounds the QPU at every layer.")
        self.wait(3.2)
        self.fade_all()


# ================================================================= 5. data layer
class S05_Data(Base):
    def construct(self):
        self.layer_intro(1)
        self.caption("Four primitives on address–data encodings.")
        prims = [("QPIE", "parallel classical–\nquantum exchange"),
                 ("VQT", "attention by a vectorized\nquantum dot product"),
                 ("ShardQ", "cut along the longest\nentanglement distance"),
                 ("NNQA", "polynomial networks →\nexact quantum arithmetic")]
        chips = VGroup()
        for n, d in prims:
            chips.add(VGroup(T(n, 30, C_DATA, "SEMIBOLD"),
                             T(d, 17, INK, line_spacing=0.9)).arrange(DOWN, buff=0.12))
        chips.arrange(RIGHT, buff=0.7, aligned_edge=UP).move_to([0.2, 1.6, 0])
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips], lag_ratio=0.25), run_time=1.6)
        self.wait(2.0)

        # --- ShardQ (left)
        self.caption("ShardQ cuts the encoding at its longest entanglement link.")
        xs = [-6.2 + 0.95 * i for i in range(6)]
        y = -0.95
        dots = VGroup(*[Dot([x, y, 0], radius=0.12, color=C_DATA) for x in xs])
        links = [(0, 1), (1, 2), (3, 4), (4, 5), (2, 5)]
        arcs = VGroup()
        for a, b in links:
            ang = -PI / 2 if b - a > 1 else -PI / 1.5
            arcs.add(ArcBetweenPoints([xs[a], y, 0], [xs[b], y, 0], angle=ang,
                                      color=C_DATA, stroke_width=2.5))
        qlab = T("qubits of one encoding", 16, MUTED).next_to(dots, DOWN, buff=0.2)
        self.play(FadeIn(dots), FadeIn(qlab), run_time=0.5)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.2), run_time=1.2)
        self.play(Indicate(arcs[-1], color=C_DATA, scale_factor=1.05), run_time=0.7)
        xc = (xs[2] + xs[5]) / 2
        cut = DashedLine([xc, y - 0.22, 0], [xc, y + 1.0, 0], color=SCARLET, stroke_width=3, dash_length=0.1)
        clab = T("cut", 16, SCARLET).next_to(cut, UP, buff=0.08)
        self.play(Create(cut), FadeIn(clab), run_time=0.5)
        left = VGroup(*dots[:3], *arcs[:2])
        right = VGroup(*dots[3:], *arcs[2:4])
        self.play(FadeOut(arcs[-1]), left.animate.shift(LEFT * 0.2), right.animate.shift(RIGHT * 0.2),
                  run_time=0.6)
        t1 = ValueTracker(0)
        c1 = counter(t1, lambda v: f"≈{v:.0f}% lower encoding error", 26, INK, "MEDIUM",
                     anchor=[-6.4, -2.3, 0], edge=LEFT)
        s1 = T("IBM Heron", 18, MUTED).move_to([-6.4, -2.7, 0], aligned_edge=LEFT)
        self.add(c1)
        self.play(t1.animate.set_value(15), FadeIn(s1), run_time=1.2)
        self.wait(1.4)

        # --- NNQA (right)
        self.caption("NNQA turns polynomial networks into exact quantum arithmetic.")
        cx, cy = 2.5, -0.85
        ax = VGroup(axis([cx - 1.4, cy, 0], [cx + 1.4, cy, 0]),
                    axis([cx - 1.3, cy - 1.05, 0], [cx - 1.3, cy + 1.05, 0]))
        axl = VGroup(T("x", 16, MUTED).next_to(ax[0], RIGHT, buff=0.08),
                     T("p(x) · degree ≤ 35", 16, MUTED).next_to(ax[1], UP, buff=0.1).align_to(ax[1], LEFT))
        pts = [[cx + 1.2 * x, cy + 2.3 * (1.6 * x ** 3 - 1.2 * x), 0] for x in np.linspace(-1, 1, 60)]
        curve = VMobject(color=C_DATA, stroke_width=3).set_points_smoothly(pts)
        self.play(Create(ax), FadeIn(axl), run_time=0.5)
        self.play(Create(curve), run_time=1.0)
        qa = box("exact quantum\narithmetic", 2.2, 0.9, C_DATA, size=17)
        qa.move_to([5.65, cy, 0])
        a1 = arrow([cx + 1.55, cy, 0], qa.get_left() + LEFT * 0.1, C_DATA)
        self.play(GrowArrow(a1), FadeIn(qa, shift=RIGHT * 0.2), run_time=0.7)
        t2 = ValueTracker(0)
        c2 = counter(t2, lambda v: f"over {v:.1f}% accuracy", 26, INK, "MEDIUM",
                     anchor=[1.1, -2.3, 0], edge=LEFT)
        s2 = T("IonQ Forte-1", 18, MUTED).move_to([1.1, -2.7, 0], aligned_edge=LEFT)
        self.add(c2)
        self.play(t2.animate.set_value(99.5), FadeIn(s2), run_time=1.4)
        self.wait(2.8)
        self.fade_all()


# ================================================================= 6. noise layer
class S06_Noise(Base):
    def construct(self):
        self.layer_intro(2)
        self.caption("DEAL maps QUBO coefficients directly to circuit angles.")

        deal = T("DEAL", 24, C_NOISE, "SEMIBOLD").move_to([-6.5, 2.0, 0], aligned_edge=LEFT)
        vals = [[0.9, 0.5, 0.2, 0.6], [0.5, 0.8, 0.4, 0.1], [0.2, 0.4, 0.7, 0.5], [0.6, 0.1, 0.5, 0.9]]
        cells = VGroup()
        for r in range(4):
            for c in range(4):
                cells.add(Square(0.42).set_fill(C_NOISE, 0.15 + 0.8 * vals[r][c]).set_stroke(BG, 1))
        cells.arrange_in_grid(rows=4, cols=4, buff=0.05).move_to([-5.1, 0.55, 0])
        qlab = T("QUBO coefficients", 20, INK).next_to(cells, DOWN, buff=0.2)
        self.play(FadeIn(deal), FadeIn(cells, lag_ratio=0.03), FadeIn(qlab), run_time=0.8)

        dials, needles = VGroup(), []
        for i, th in enumerate([35, 120, 70]):
            c = np.array([-2.1 + 1.0 * i, 0.55, 0])
            ring = Circle(radius=0.34, color=C_NOISE, stroke_width=2).move_to(c)
            needle = Line(c, c + RIGHT * 0.3, color=INK, stroke_width=3)
            lab = T(f"θ{'₁₂₃'[i]}", 18, INK).next_to(ring, DOWN, buff=0.12)
            dials.add(VGroup(ring, needle, lab))
            needles.append((needle, th, c))
        alab = T("circuit angles", 20, INK).next_to(dials, UP, buff=0.2)
        a1 = arrow(cells.get_right() + RIGHT * 0.15, dials.get_left() + LEFT * 0.15, C_NOISE)
        bb = box("black-box optimizer", None, 0.5, MUTED, size=16, text_color=MUTED)
        bb.move_to([-2.35, -1.1, 0])
        cross = Cross(bb, stroke_color=SCARLET, stroke_width=3)
        self.play(GrowArrow(a1), FadeIn(dials), FadeIn(alab), run_time=0.8)
        self.play(*[Rotate(n, th * DEGREES, about_point=c) for n, th, c in needles], run_time=0.8)
        self.play(FadeIn(bb), run_time=0.4)
        self.play(Create(cross), run_time=0.4)
        self.wait(1.2)

        # gain bar
        self.caption("Up to 14.81% higher ground-state success than QAOA.")
        BX, BY = -6.2, -2.1
        unit = 4.4 / 15
        t = ValueTracker(0)
        bar = hbar(t, BX, BY, 0.5, unit, C_NOISE)
        bax = axis([BX, BY - 0.35, 0], [BX + 4.6, BY - 0.35, 0])
        bt = VGroup()
        for pct in [0, 5, 10, 15]:
            x = BX + pct * unit
            bt.add(Line([x, BY - 0.35, 0], [x, BY - 0.45, 0], color=MUTED, stroke_width=2),
                   T(f"{pct}%", 15, MUTED).next_to([x, BY - 0.45, 0], DOWN, buff=0.06))
        blab = T("ground-state success gain over QAOA", 16, MUTED).move_to([BX, BY + 0.55, 0], aligned_edge=LEFT)
        cnt = counter(t, lambda v: f"+{v:.2f}%", 26, INK, "MEDIUM", anchor=[BX + 4.75, BY, 0], edge=LEFT)
        hw = T("IBM Heron", 15, MUTED).move_to([BX + 4.75, BY - 0.4, 0], aligned_edge=LEFT)
        self.play(Create(bax), FadeIn(bt), FadeIn(blab), run_time=0.5)
        self.add(bar, cnt)
        self.play(t.animate.set_value(14.81), FadeIn(hw), run_time=1.5)
        self.wait(1.4)

        # QAWA convergence
        self.caption("QAWA converges in about 75 iterations.")
        OX, OY, W, H = 1.3, -1.9, 5.2, 3.4
        xax = axis([OX, OY, 0], [OX + W + 0.2, OY, 0])
        yax = axis([OX, OY, 0], [OX, OY + H + 0.2, 0])
        xt = VGroup()
        for it in [0, 25, 50, 75, 100]:
            x = OX + W * it / 100
            xt.add(Line([x, OY, 0], [x, OY - 0.1, 0], color=MUTED, stroke_width=2),
                   T(str(it), 15, MUTED).next_to([x, OY - 0.1, 0], DOWN, buff=0.06))
        xl = T("iteration", 18, MUTED).move_to([OX + W / 2, OY - 0.7, 0])
        yl = T("cost", 18, MUTED).rotate(PI / 2).next_to(yax, LEFT, buff=0.12)
        ql = T("QAWA", 24, C_NOISE, "SEMIBOLD").move_to([OX + W - 0.1, OY + H - 0.1, 0], aligned_edge=UR)
        pts = [[OX + W * it / 100, OY + H * (0.12 + 0.88 * np.exp(-it / 22)), 0]
               for it in np.linspace(0, 100, 80)]
        curve = VMobject(color=C_NOISE, stroke_width=3).set_points_smoothly(pts)
        x75 = OX + W * 0.75
        vline = DashedLine([x75, OY, 0], [x75, OY + H * 0.75, 0], color=INK, stroke_width=2, dash_length=0.1)
        vlab = T("≈ 75 iterations", 18, INK).next_to(vline, UP, buff=0.1)
        self.play(Create(xax), Create(yax), FadeIn(xt), FadeIn(xl), FadeIn(yl), FadeIn(ql), run_time=0.7)
        self.play(Create(curve), run_time=2.0, rate_func=linear)
        self.play(Create(vline), FadeIn(vlab), run_time=0.6)
        self.wait(3.0)
        self.fade_all()


# ================================================================= 7. synthesis layer
class S07_Synthesis(Base):
    def construct(self):
        self.layer_intro(3)
        self.caption("RubriQ fine-tunes a 7B code model with GRPO against a rubric.")

        # the reward loop
        P = {"model": [-5.5, 0.85, 0], "circ": [-3.4, 2.1, 0], "sim": [-1.3, 0.85, 0], "rew": [-3.4, -0.4, 0]}
        nodes = {"model": box("7B code model", None, 0.55, C_SYNTH),
                 "circ": box("circuit", None, 0.55, C_SYNTH),
                 "sim": box("CUDA-Q simulation", None, 0.55, C_SYNTH),
                 "rew": box("rubric reward", None, 0.55, C_SYNTH)}
        for k, v in nodes.items():
            v.move_to(P[k])
        order = ["model", "circ", "sim", "rew"]
        arrows = VGroup()
        for a, b in zip(order, order[1:] + order[:1]):
            s, e = nodes[a], nodes[b]
            d = e.get_center() - s.get_center()
            d = d / np.linalg.norm(d)
            arrows.add(arrow(edge_point(s, d), edge_point(e, -d), C_SYNTH, sw=2.5, tip=0.16))
        grpo = T("GRPO", 16, C_SYNTH, "SEMIBOLD").next_to(arrows[3], LEFT, buff=0.08).shift(DOWN * 0.1)
        for i, k in enumerate(order):
            self.play(FadeIn(nodes[k], scale=0.8), run_time=0.35)
            self.play(GrowArrow(arrows[i]), run_time=0.3)
        self.play(FadeIn(grpo), run_time=0.3)
        path = VMobject().set_points_as_corners([P["model"], P["circ"], P["sim"], P["rew"], P["model"]])
        tok = Dot(radius=0.09, color=WHITE).move_to(P["model"])
        self.add(tok)
        self.play(MoveAlongPath(tok, path), run_time=1.8, rate_func=linear)
        self.play(FadeOut(tok), run_time=0.2)
        self.wait(0.6)

        # the rubric
        self.caption("Five rubric terms, scored by CUDA-Q simulation inside the reward loop.")
        rub = [("fidelity", 0.40), ("Clifford fraction", 0.20), ("hardware compliance", 0.15),
               ("T-count", 0.15), ("efficiency", 0.10)]
        rt_ = T("five-term rubric · weights", 18, MUTED).move_to([-6.4, -1.1, 0], aligned_edge=LEFT)
        rows = VGroup()
        for i, (n, w) in enumerate(rub):
            y = -1.45 - 0.3 * i
            lab = T(n, 16, INK).next_to([-3.9, y, 0], LEFT, buff=0)
            bar = (Rectangle(width=w * 5.0, height=0.2).set_fill(C_SYNTH, 0.95 - 0.13 * i)
                   .set_stroke(width=0).move_to([-3.75, y, 0], aligned_edge=LEFT))
            val = T(f"{w:.2f}", 16, INK).next_to(bar, RIGHT, buff=0.12)
            rows.add(VGroup(lab, bar, val))
        self.play(FadeIn(rt_), run_time=0.3)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(r[0]), GrowFromEdge(r[1], LEFT), FadeIn(r[2]))
                                for r in rows], lag_ratio=0.3), run_time=1.8)
        self.wait(1.6)

        # T-gate compression
        self.caption("3.31× mean T-gate compression; hardware violations below 1%.")
        OX, OY, unit = 1.8, -2.4, 0.95
        yax = axis([OX, OY, 0], [OX, OY + 4 * unit + 0.1, 0])
        xax = axis([OX, OY, 0], [OX + 4.6, OY, 0])
        yt = VGroup()
        for k in range(5):
            y = OY + k * unit
            yt.add(Line([OX - 0.1, y, 0], [OX, y, 0], color=MUTED, stroke_width=2),
                   T(f"{k}×", 15, MUTED).next_to([OX - 0.1, y, 0], LEFT, buff=0.06))
        yl = T("mean T-gate compression", 18, MUTED).move_to([OX - 0.35, OY + 4 * unit + 0.45, 0], aligned_edge=LEFT)
        self.play(Create(yax), Create(xax), FadeIn(yt), FadeIn(yl), run_time=0.6)
        series = [("sparse-reward RL", 2.05, 0.45, OX + 1.2), ("RubriQ", 3.31, 0.95, OX + 3.2)]
        for name, v, op, x in series:
            t = ValueTracker(0)
            bar = vbar(t, x, OY, 1.2, unit, C_SYNTH, op)
            lab = T(name, 17, INK).next_to([x, OY, 0], DOWN, buff=0.15)
            c = counter(t, lambda u: f"{u:.2f}×", 24, INK, "MEDIUM",
                        anchor=[x, OY + v * unit + 0.15, 0], edge=DOWN)
            self.add(bar)
            self.play(FadeIn(lab), run_time=0.3)
            self.add(c)
            self.play(t.animate.set_value(v), run_time=1.1)
        viol = T("hardware violations < 1%", 20, INK).move_to([OX + 2.3, OY + 4 * unit + 1.1, 0])
        self.play(FadeIn(viol, shift=UP * 0.1), run_time=0.5)
        self.wait(3.0)
        self.fade_all()


# ================================================================= 8. trust mechanism
def encoder_panel(cx, title):
    hdr = T(title, 26, INK, "MEDIUM").move_to([cx, 2.05, 0])
    body = RoundedRectangle(corner_radius=0.2, width=5.6, height=1.5).set_stroke(C_TRUST, 2).set_fill(BG, 1)
    body.move_to([cx, 0.8, 0])
    dots = VGroup(*[Dot([cx - 2.17 + 0.62 * i, 0.8, 0], radius=0.14, color=C_TRUST) for i in range(8)])
    lab = T("8-qubit encoder", 16, MUTED).next_to(body, DOWN, buff=0.1).align_to(body, RIGHT)
    inj = box("co-located fault injector", None, 0.5, MUTED, size=17).move_to([cx, -1.5, 0])
    g = VGroup(hdr, body, dots, lab, inj)
    g.hdr, g.body, g.dots, g.lab, g.inj = hdr, body, dots, lab, inj
    return g


class S08_TrustMechanism(Base):
    def construct(self):
        self.layer_intro(4)
        self.caption("A fixed, public QEC encoder is a reusable target.")
        L = encoder_panel(-3.5, "fixed encoder")
        R = encoder_panel(3.5, "reseeded encoder")
        self.play(FadeIn(L.hdr), FadeIn(L.body), FadeIn(L.dots), FadeIn(L.lab), run_time=0.6)
        self.play(FadeIn(L.inj, shift=UP * 0.2), run_time=0.4)
        lring = Circle(radius=0.23, color=SCARLET, stroke_width=2.5).move_to(L.dots[2])
        wlab = T("weak spot", 15, SCARLET).next_to(lring, UP, buff=0.08)
        self.play(Create(lring), FadeIn(wlab), run_time=0.5)
        self.wait(1.2)
        self.play(FadeIn(R.hdr), FadeIn(R.body), FadeIn(R.dots), FadeIn(R.lab), FadeIn(R.inj), run_time=0.6)
        rring = Circle(radius=0.23, color=SCARLET, stroke_width=2.5).move_to(R.dots[2])
        self.play(Create(rring), run_time=0.4)
        self.caption("Reseed the encoder every run: the weak spot moves.")
        self.wait(0.6)

        acc, rej = ValueTracker(0), ValueTracker(0)
        ac = counter(acc, lambda v: f"accepted  {int(round(v))}", 20, INK, anchor=[-3.5, -2.3, 0])
        rc = counter(rej, lambda v: f"rejected  {int(round(v))}", 20, INK, anchor=[3.5, -2.3, 0])
        self.add(ac, rc)
        seed = T("↻ new seed", 15, INK).next_to(R.body, UP, buff=0.08).align_to(R.body, RIGHT)
        seq = [5, 0, 6]
        for run in range(3):
            self.play(rring.animate.move_to(R.dots[seq[run]]), FadeIn(seed), run_time=0.5)
            la = arrow(L.inj.get_top(), L.dots[2].get_center() + DOWN * 0.2, SCARLET, sw=3, tip=0.18)
            ra = arrow(R.inj.get_top(), R.dots[2].get_center() + DOWN * 0.2, SCARLET, sw=3, tip=0.18)
            self.play(GrowArrow(la), GrowArrow(ra), FadeOut(seed), run_time=0.45)
            hit = T("accepted", 15, SCARLET).next_to(L.dots[2], DOWN, buff=0.2)
            miss = T("rejected", 15, INK).next_to(R.dots[2], DOWN, buff=0.2)
            xm = Cross(scale_factor=0.16, stroke_color=INK, stroke_width=3).move_to(ra.get_end() + DOWN * 0.1)
            self.play(Flash(L.dots[2], color=SCARLET, flash_radius=0.3, line_length=0.18),
                      FadeIn(hit), FadeIn(miss), FadeIn(xm), ra.animate.set_color(MUTED),
                      acc.animate.set_value(run + 1), rej.animate.set_value(run + 1), run_time=0.5)
            self.wait(0.45)
            self.play(FadeOut(la), FadeOut(ra), FadeOut(hit), FadeOut(miss), FadeOut(xm), run_time=0.3)
        self.wait(0.4)
        self.caption("Hadamard-structured ensemble · seeded Clifford circuits")
        self.wait(3.0)
        self.fade_all()


# ================================================================= 9. trust result
class S09_TrustResult(Base):
    def construct(self):
        small = self.small_map(4)
        hdr = self.layer_header(4, small)
        self.add(small, hdr)
        self.caption("Reseeding cuts the accepted logical disturbance.")

        OX, OY, unit = -4.8, -2.3, 20.0      # 0.150 -> 3.0 units
        yax = axis([OX, OY, 0], [OX, OY + 0.15 * unit + 0.25, 0])
        xax = axis([OX, OY, 0], [OX + 4.0, OY, 0])
        yt = VGroup()
        for v in [0, 0.05, 0.10, 0.15]:
            y = OY + v * unit
            yt.add(Line([OX - 0.1, y, 0], [OX, y, 0], color=MUTED, stroke_width=2),
                   T(f"{v:.2f}", 15, MUTED).next_to([OX - 0.1, y, 0], LEFT, buff=0.06))
        yl = T("mean accepted logical disturbance · eight-qubit encoders", 16, MUTED)
        yl.move_to([OX - 0.6, OY + 0.15 * unit + 0.95, 0], aligned_edge=LEFT)
        self.play(Create(yax), Create(xax), FadeIn(yt), FadeIn(yl), run_time=0.7)
        series = [("fixed", 0.150, 0.45, OX + 1.2), ("reseeded", 0.020, 0.95, OX + 3.0)]
        for name, v, op, x in series:
            t = ValueTracker(0)
            bar = vbar(t, x, OY, 1.2, unit, C_TRUST, op)
            lab = T(name, 18, INK).next_to([x, OY, 0], DOWN, buff=0.15)
            c = counter(t, lambda u: f"{u:.3f}", 24, INK, "MEDIUM", anchor=[x, OY + v * unit + 0.15, 0], edge=DOWN)
            self.add(bar)
            self.play(FadeIn(lab), run_time=0.3)
            self.add(c)
            self.play(t.animate.set_value(v), run_time=1.2)
            self.wait(0.3)
        big = ValueTracker(0)
        bc = counter(big, lambda u: f"−{u:.1f}%", 64, INK, "SEMIBOLD", anchor=[3.4, 1.3, 0])
        bl = T("accepted disturbance", 22, MUTED).move_to([3.4, 0.5, 0])
        self.add(bc)
        self.play(big.animate.set_value(86.7), FadeIn(bl), run_time=1.4)
        self.wait(1.6)

        # the PQC module
        self.caption("Seeds and keys come from a post-quantum cryptographic module.")
        mod = RoundedRectangle(corner_radius=0.18, width=5.0, height=1.65).set_stroke(C_TRUST, 2).set_fill(BG, 1)
        mod.move_to([3.6, -1.5, 0])
        mt = T("post-quantum cryptographic module", 17, INK).move_to(mod.get_top() + DOWN * 0.32)
        ms = T("designed to FIPS 140-3", 15, MUTED).next_to(mt, DOWN, buff=0.08)
        chips = VGroup(*[box(n, 1.35, 0.42, C_TRUST, size=15) for n in ["ML-KEM", "ML-DSA", "SLH-DSA"]])
        chips.arrange(RIGHT, buff=0.15).move_to(mod.get_bottom() + UP * 0.4)
        ka = arrow(mod.get_left() + LEFT * 0.05, [-0.5, -1.5, 0], C_TRUST, sw=2.5, tip=0.16)
        kl = T("seeds & keys", 15, INK).next_to(ka, UP, buff=0.08)
        self.play(FadeIn(mod), FadeIn(mt), FadeIn(ms), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in chips], lag_ratio=0.3), run_time=0.8)
        self.play(GrowArrow(ka), FadeIn(kl), run_time=0.5)
        self.wait(3.2)
        self.fade_all()


# ================================================================= 10. closing
class S10_Closing(Base):
    def construct(self):
        m = StackMap().shift(DOWN * 0.1)
        self.play(GrowFromCenter(m.qpu_circle), FadeIn(m.qpu_text), run_time=0.6)
        anims = []
        for i in range(5):
            d = m.dirs[i]
            sec, lab = m.sectors[i], m.labels[i]
            sec.save_state()
            sec.shift(d * 4.5).set_opacity(0)
            anims.append(AnimationGroup(Restore(sec), FadeIn(lab, shift=-d * 0.3)))
        self.play(LaggedStart(*anims, lag_ratio=0.15), run_time=1.8)
        self.caption("Useful quantum computation comes from a co-designed stack.")
        self.wait(2.4)
        self.caption("Classical HPC surrounds the QPU at every layer.")
        self.wait(2.6)
        self.clear_caption(0.4)
        self.play(m.animate.scale(0.62).shift(UP * 1.1), run_time=1.0)
        line = T("The stack is the machine.", 54, WHITE, "SEMIBOLD").move_to([0, -2.1, 0])
        rule = Line(LEFT * 1.6, RIGHT * 1.6, color=SCARLET, stroke_width=4).next_to(line, DOWN, buff=0.3)
        self.play(Write(line), run_time=1.6)
        self.play(GrowFromCenter(rule), run_time=0.5)
        self.wait(3.2)
        self.play(FadeOut(m), FadeOut(line), FadeOut(rule), run_time=0.8)
        end = VGroup(T("Ziqing Guo", 34, INK, "MEDIUM"),
                     T("Texas Tech University · Computer Science · 2026", 22, MUTED)).arrange(DOWN, buff=0.2)
        self.play(FadeIn(end), run_time=0.8)
        self.wait(2.4)
        self.play(FadeOut(end), run_time=0.8)


SCENES = ["S01_Title", "S02_MemoryWall", "S03_QGear", "S04_Stack", "S05_Data",
          "S06_Noise", "S07_Synthesis", "S08_TrustMechanism", "S09_TrustResult", "S10_Closing"]


# ================================================================= render + concat
def main():
    import argparse
    import os
    import subprocess
    import sys
    from concurrent.futures import ThreadPoolExecutor

    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Render every scene and concatenate them.")
    ap.add_argument("--quality", default="m", choices=["l", "m", "h"])
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--media_dir", default=os.path.join(here, "_media"))
    ap.add_argument("--out", default=os.path.join(here, "thesis_explainer.mp4"))
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()

    os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")
    scenes = args.only or SCENES
    folder = {"l": "480p30", "m": "720p30", "h": "1080p30"}[args.quality]

    def render(scene):
        cmd = [sys.executable, "-m", "manim", "render", "-q", args.quality, "--fps", "30",
               "--disable_caching", "--media_dir", args.media_dir, __file__, scene]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = r.returncode == 0
        print(("ok   " if ok else "FAIL ") + scene, flush=True)
        if not ok:
            print(r.stdout[-3000:], r.stderr[-3000:])
        return ok

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(render, scenes))
    if not all(results):
        sys.exit("some scenes failed")

    # Always concatenate the full film; --only just limits what gets re-rendered.
    vid_dir = os.path.join(args.media_dir, "videos", "explainer", folder)
    missing = [s for s in SCENES if not os.path.exists(os.path.join(vid_dir, s + ".mp4"))]
    if missing:
        sys.exit("missing renders for: " + ", ".join(missing))
    lst = os.path.join(args.media_dir, "concat.txt")
    with open(lst, "w") as f:
        for s in SCENES:
            f.write(f"file '{os.path.join(vid_dir, s + '.mp4')}'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", "-movflags", "+faststart", args.out], check=True)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
