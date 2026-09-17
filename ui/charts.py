import tkinter as tk
from ui.theme import (
    BG_CARD,
    BORDER,
    TEXT_MUTED,
    ACCENT_BLUE,
    ACCENT_AMBER,
    ACCENT_GREEN,
    FONT_BOLD,
    FONT_SM,
    FONT_XS,
)

class QueueChart(tk.Canvas):
    def __init__(self, parent):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightthickness=1,
            highlightbackground=BORDER,
            bd=0
        )

    def render(self, steps):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 100:
            w = 440
        if h < 100:
            h = 210

        num_steps = len(steps)
        max_q = max([s["queue"] for s in steps] + [8])

        pad_l, pad_r, pad_t, pad_b = 40, 16, 28, 30
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        self.create_text(
            pad_l, 14,
            anchor=tk.W,
            text="PASSENGER QUEUE ACCUMULATION WAVE",
            font=FONT_BOLD,
            fill=ACCENT_BLUE
        )

        for g in range(0, max_q + 1, max(1, max_q // 4)):
            gy = pad_t + plot_h - int((g / max_q) * plot_h)
            self.create_line(pad_l, gy, w - pad_r, gy, fill="#1f293d", width=1)
            self.create_text(pad_l - 6, gy, text=str(g), font=FONT_XS, fill=TEXT_MUTED, anchor=tk.E)

        pts = []
        for s in steps:
            x = pad_l + int((s["minute"] / (num_steps - 1 if num_steps > 1 else 1)) * plot_w)
            y = pad_t + plot_h - int((s["queue"] / max_q) * plot_h)
            pts.append((x, y, s))

        if len(pts) > 1:
            poly = [pad_l, pad_t + plot_h]
            for x, y, _ in pts:
                poly.extend([x, y])
            poly.extend([pts[-1][0], pad_t + plot_h])
            self.create_polygon(poly, fill="#082f49", outline="")

            line_coords = []
            for x, y, _ in pts:
                line_coords.extend([x, y])
            self.create_line(line_coords, fill=ACCENT_BLUE, width=2)

        for x, y, s in pts:
            if s["jeepney_arrived"]:
                self.create_oval(x - 5, y - 5, x + 5, y + 5, fill=ACCENT_GREEN, outline="#ffffff", width=1)
            else:
                self.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#0284c7", outline="")

        self.create_line(pad_l, pad_t + plot_h, w - pad_r, pad_t + plot_h, fill="#475569", width=1)
        self.create_text(w // 2, h - 10, text="Simulation Minutes", font=FONT_XS, fill=TEXT_MUTED)

class InflowChart(tk.Canvas):
    def __init__(self, parent):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightthickness=1,
            highlightbackground=BORDER,
            bd=0
        )

    def render(self, steps):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 100:
            w = 440
        if h < 100:
            h = 210

        num_steps = len(steps)
        pad_l, pad_r, pad_t, pad_b = 40, 16, 28, 30
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        self.create_text(
            pad_l, 14,
            anchor=tk.W,
            text="PASSENGER INFLOW PER MINUTE (LCM STOCHASTIC)",
            font=FONT_BOLD,
            fill=ACCENT_AMBER
        )

        for g in range(0, 5):
            gy = pad_t + plot_h - int((g / 4) * plot_h)
            self.create_line(pad_l, gy, w - pad_r, gy, fill="#1f293d", width=1)
            self.create_text(pad_l - 6, gy, text=str(g), font=FONT_XS, fill=TEXT_MUTED, anchor=tk.E)

        bar_width = max(3, int(plot_w / num_steps) - 2)
        for s in steps:
            if s["minute"] == 0:
                continue
            bx = pad_l + int((s["minute"] / num_steps) * plot_w)
            by = pad_t + plot_h - int((s["arrivals"] / 4) * plot_h)
            self.create_rectangle(bx, by, bx + bar_width, pad_t + plot_h, fill=ACCENT_AMBER, outline="#b45309")

        self.create_line(pad_l, pad_t + plot_h, w - pad_r, pad_t + plot_h, fill="#475569", width=1)
        self.create_text(w // 2, h - 10, text="Simulation Minutes", font=FONT_XS, fill=TEXT_MUTED)
