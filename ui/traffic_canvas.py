import tkinter as tk
from ui.theme import (
    ROAD_ASPHALT,
    ROAD_LANE,
    ROAD_LINE,
    BAY_BG,
    BAY_BORDER,
    PLATFORM_BG,
    ACCENT_BLUE,
    ACCENT_AMBER,
    ACCENT_GREEN,
    TEXT_MAIN,
    TEXT_MUTED,
    FONT_BOLD,
    FONT_SM,
    FONT_XS,
)

class TrafficCanvas(tk.Canvas):
    def __init__(self, parent, height=185):
        super().__init__(
            parent,
            height=height,
            bg=ROAD_ASPHALT,
            highlightthickness=1,
            highlightbackground="#2d374e",
            bd=0
        )

    def render(self, step, parameters):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 100:
            w = 900
        if h < 100:
            h = 185

        cap = parameters["jeepney_capacity"]
        interval = parameters["jeepney_interval"]
        arrived = step["jeepney_arrived"]
        minute = step["minute"]
        queue_count = step["queue"]

        self.create_rectangle(0, 0, w, h, fill=ROAD_ASPHALT, outline="")
        self.create_rectangle(0, 130, w, h, fill=ROAD_LANE, outline="")

        dash_x = 0
        while dash_x < w:
            self.create_line(dash_x, 130, dash_x + 24, 130, fill=ROAD_LINE, width=2)
            dash_x += 42

        for arrow_x in range(120, w - 60, 240):
            self.create_line(arrow_x, 155, arrow_x + 30, 155, arrow=tk.LAST, fill="#475569", width=3)
            self.create_text(arrow_x + 15, 170, text="ESPAÑA BLVD (EASTBOUND)", font=FONT_XS, fill="#64748b")

        self.create_rectangle(0, 72, w, 130, fill="#1c2433", outline="")
        self.create_line(0, 130, w, 130, fill=ACCENT_AMBER, width=1)

        hatch_x = 8
        while hatch_x < w:
            self.create_line(hatch_x, 130, hatch_x + 28, 72, fill="#273246", width=2)
            hatch_x += 38

        self.create_text(65, 100, text="PUV ONLY", font=FONT_BOLD, fill=ACCENT_AMBER)
        self.create_text(w - 85, 100, text="BUS & JEEPNEY BAY", font=FONT_SM, fill=ACCENT_AMBER)

        self.create_rectangle(0, 0, w, 72, fill=PLATFORM_BG, outline="")
        self.create_rectangle(0, 69, w, 72, fill="#94a3b8", outline="")

        for zx in range(12, 54, 8):
            self.create_rectangle(zx, 72, zx + 4, h, fill="#f8fafc", outline="")

        self.create_rectangle(75, 6, 350, 66, fill="#1e293b", outline=ACCENT_BLUE, width=1)
        self.create_rectangle(78, 9, 347, 23, fill="#0f172a", outline="")
        self.create_text(86, 16, anchor=tk.W, text="TERMINAL WAITING PLATFORM • QUIAPO ROUTE", font=FONT_XS, fill=ACCENT_BLUE)

        self.create_text(86, 32, anchor=tk.W, text=f"ACTIVE QUEUE: {queue_count} COMMUTERS", font=FONT_BOLD, fill=TEXT_MAIN)

        px = 86
        py = 43
        max_icons = min(queue_count, 32)
        for _ in range(max_icons):
            self.create_oval(px, py, px + 5, py + 5, fill=ACCENT_BLUE, outline="")
            self.create_rectangle(px - 1, py + 6, px + 6, py + 12, fill="#0284c7", outline="")
            px += 8
            if px > 336:
                px = 86
                py += 10

        if queue_count == 0:
            self.create_text(86, 48, anchor=tk.W, text="Platform clear • Zero waiting commuters", font=FONT_XS, fill=TEXT_MUTED)
        elif queue_count > 32:
            self.create_text(px + 4, py + 3, anchor=tk.W, text=f"+{queue_count - 32} more", font=FONT_XS, fill=ACCENT_AMBER)

        self.create_line(360, 36, 395, 36, arrow=tk.LAST, fill=ACCENT_AMBER, width=2)
        self.create_text(378, 26, text="BOARD", font=FONT_XS, fill=ACCENT_AMBER)

        bay_x = 410
        bay_w = min(460, w - bay_x - 20)

        if arrived:
            self.create_rectangle(bay_x, 76, bay_x + bay_w, 126, fill=BAY_BG, outline=BAY_BORDER, width=2)

            jx = bay_x + 12
            jy = 81
            jw = min(350, bay_w - 24)
            jh = 38

            self.create_rectangle(jx + 20, jy - 3, jx + 40, jy, fill="#0f172a", outline="#475569")
            self.create_rectangle(jx + jw - 55, jy - 3, jx + jw - 35, jy, fill="#0f172a", outline="#475569")
            self.create_rectangle(jx + 20, jy + jh, jx + 40, jy + jh + 3, fill="#0f172a", outline="#475569")
            self.create_rectangle(jx + jw - 55, jy + jh, jx + jw - 35, jy + jh + 3, fill="#0f172a", outline="#475569")

            self.create_rectangle(jx, jy, jx + jw, jy + jh, fill="#eab308", outline="#78350f", width=2)
            self.create_rectangle(jx + jw - 36, jy + 3, jx + jw - 2, jy + jh - 3, fill="#fef08a", outline="#b45309")
            self.create_text(jx + jw - 18, jy + jh // 2, text="CAB", font=FONT_XS, fill="#78350f")

            self.create_rectangle(jx + jw - 50, jy + 5, jx + jw - 38, jy + jh - 5, fill="#0f172a", outline=ACCENT_BLUE)
            self.create_oval(jx + jw - 2, jy + 3, jx + jw + 2, jy + 9, fill="#fef08a", outline="")
            self.create_oval(jx + jw - 2, jy + jh - 9, jx + jw + 2, jy + jh - 3, fill="#fef08a", outline="")

            self.create_rectangle(jx + 12, jy + 2, jx + jw - 55, jy + 11, fill="#0f172a", outline=ACCENT_AMBER)
            self.create_text(jx + (jw - 43) // 2, jy + 6, text="QUIAPO - CUBAO EXPRESS", font=FONT_XS, fill=ACCENT_BLUE)

            seat_w = min(24, (jw - 75) // max(1, cap))
            sx = jx + 12
            sy = jy + 15
            for s in range(1, cap + 1):
                occupied = (s <= step["served"])
                s_bg = ACCENT_GREEN if occupied else "#334155"
                s_border = "#047857" if occupied else "#64748b"
                self.create_rectangle(sx, sy, sx + seat_w - 3, sy + 18, fill=s_bg, outline=s_border)
                self.create_text(
                    sx + (seat_w - 3) // 2,
                    sy + 9,
                    text=f"P{s}" if occupied else f"{s}",
                    font=FONT_XS,
                    fill="#ffffff" if occupied else "#94a3b8"
                )
                sx += seat_w

            self.create_text(
                bay_x + bay_w // 2,
                66,
                text=f"JEEPNEY DOCKED • Boarded {step['served']} / {cap} passengers",
                font=FONT_BOLD,
                fill=ACCENT_GREEN
            )
        else:
            rem = interval - (minute % interval)
            self.create_rectangle(bay_x, 76, bay_x + bay_w, 126, fill="#17202f", outline="#2e3b52", width=1)
            self.create_text(
                bay_x + bay_w // 2,
                92,
                text=f"BAY VACANT • NEXT ARRIVAL IN {rem} MINUTE(S)",
                font=FONT_BOLD,
                fill=TEXT_MUTED
            )

            bar_w = min(220, bay_w - 40)
            bx = bay_x + (bay_w - bar_w) // 2
            by = 108
            prog = (interval - rem) / interval
            self.create_rectangle(bx, by, bx + bar_w, by + 7, fill="#0f172a", outline="#334155")
            self.create_rectangle(bx, by, bx + int(bar_w * prog), by + 7, fill=ACCENT_BLUE, outline="")

            self.create_text(
                bay_x + bay_w // 2,
                66,
                text=f"Scheduled Fleet Headway: 1 Jeepney every {interval} mins",
                font=FONT_XS,
                fill=TEXT_MUTED
            )
