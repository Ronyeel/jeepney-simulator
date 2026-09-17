import sys
import tkinter as tk
from tkinter import ttk, messagebox

from simulation import run_simulation
from ui.theme import (
    BG_ROOT,
    BG_PANEL,
    BG_CARD,
    BORDER,
    TEXT_MAIN,
    TEXT_MUTED,
    ACCENT_BLUE,
    ACCENT_AMBER,
    ACCENT_GREEN,
    FONT_TITLE,
    FONT_SUB,
    FONT_BOLD,
    FONT_REG,
    FONT_MONO,
    FONT_MONO_BOLD,
    FONT_SM,
    FONT_XS,
)
from ui.traffic_canvas import TrafficCanvas
from ui.charts import QueueChart, InflowChart
from ui.panels import ParametersPanel, EulerAuditPanel, KpiBar, MathTracePanel
from ui.table_view import TelemetryTable

PRESETS = {
    "default": {"name": "Default (c=5, Suboptimal)", "seed": 13, "a": 21, "c": 5, "m": 100, "dur": 30, "int": 5, "cap": 8},
    "optimal": {"name": "Optimal (c=7, Full Period)", "seed": 13, "a": 21, "c": 7, "m": 100, "dur": 30, "int": 5, "cap": 8},
    "rush":    {"name": "Rush Hour (45m, Peak)", "seed": 7, "a": 17, "c": 11, "m": 100, "dur": 45, "int": 4, "cap": 10},
    "textbook":{"name": "Classroom Textbook (m=16)", "seed": 1, "a": 5, "c": 3, "m": 16, "dur": 20, "int": 4, "cap": 6}
}

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Metro Transit Simulator | A/B Street Urban Queue Planning Engine")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = min(1260, max(920, int(screen_w * 0.90)))
        win_h = min(820, max(560, int(screen_h * 0.86)))
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)

        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.minsize(880, 540)
        self.root.configure(bg=BG_ROOT)

        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(700, self._release_topmost)
        self.root.focus_force()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._configure_ttk_styles()

        self.sim_data = None
        self.current_minute = 0
        self.is_playing = False
        self.play_job = None
        self.play_speed_ms = 700

        self._build_ui()
        self.load_preset("default")

    def _release_topmost(self):
        try:
            self.root.attributes("-topmost", False)
        except Exception:
            pass

    def _on_close(self):
        self.stop_play()
        self.root.destroy()
        sys.exit(0)

    def _configure_ttk_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self.style.configure(".", font=FONT_REG, background=BG_PANEL, foreground=TEXT_MAIN)
        self.style.configure("Treeview",
            background="#1e2638",
            foreground=TEXT_MAIN,
            fieldbackground="#1e2638",
            rowheight=22,
            font=FONT_REG
        )
        self.style.configure("Treeview.Heading",
            background="#0f172a",
            foreground=ACCENT_BLUE,
            font=FONT_BOLD
        )
        self.style.map("Treeview", background=[("selected", "#0284c7")], foreground=[("selected", "#ffffff")])

    def _build_ui(self):
        top_bar = tk.Frame(self.root, bg="#0b0f19", padx=12, pady=8, bd=1, relief=tk.SOLID, highlightbackground=BORDER)
        top_bar.pack(fill=tk.X)

        title_box = tk.Frame(top_bar, bg="#0b0f19")
        title_box.pack(side=tk.LEFT)

        tk.Label(title_box, text="METRO TRANSIT SIMULATOR  [A/B STREET TRAFFIC ENGINE]", font=FONT_TITLE, fg=ACCENT_BLUE, bg="#0b0f19").pack(anchor=tk.W)
        tk.Label(title_box, text="Discrete-Event Queue Simulation • Linear Congruential Method (LCM) & Euler's Phi Totient φ(n)", font=FONT_SUB, fg=TEXT_MUTED, bg="#0b0f19").pack(anchor=tk.W)

        preset_box = tk.Frame(top_bar, bg="#0b0f19")
        preset_box.pack(side=tk.RIGHT)

        tk.Label(preset_box, text="● ENGINE READY", font=FONT_BOLD, fg=ACCENT_GREEN, bg="#064e3b", padx=6, pady=2).pack(side=tk.RIGHT, padx=(10, 0))
        tk.Label(preset_box, text="PRESETS:", font=FONT_BOLD, fg=TEXT_MUTED, bg="#0b0f19").pack(side=tk.LEFT, padx=(0, 4))

        for k, p in PRESETS.items():
            b = tk.Button(
                preset_box,
                text=p["name"],
                font=FONT_SM,
                bg=BG_PANEL,
                fg=TEXT_MAIN,
                activebackground=ACCENT_BLUE,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=1,
                padx=5,
                pady=1,
                command=lambda key=k: self.load_preset(key)
            )
            b.pack(side=tk.LEFT, padx=2)

        body = tk.Frame(self.root, bg=BG_ROOT, padx=8, pady=6)
        body.pack(fill=tk.BOTH, expand=True)

        left_pane = tk.Frame(body, bg=BG_ROOT, width=310)
        left_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        left_pane.pack_propagate(False)

        self.param_panel = ParametersPanel(left_pane, on_run=self.run_sim, on_reset=lambda: self.load_preset("default"))
        self.param_panel.pack(fill=tk.X, pady=(0, 6))

        self.euler_panel = EulerAuditPanel(left_pane)
        self.euler_panel.pack(fill=tk.BOTH, expand=True)

        right_pane = tk.Frame(body, bg=BG_ROOT)
        right_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_hud(right_pane)

        self.traffic_canvas = TrafficCanvas(right_pane, height=185)
        self.traffic_canvas.pack(fill=tk.X, pady=(0, 4))

        self.kpi_bar = KpiBar(right_pane)
        self.kpi_bar.pack(fill=tk.X, pady=(0, 4))

        self.math_trace = MathTracePanel(right_pane)
        self.math_trace.pack(fill=tk.X, pady=(0, 4))

        self._build_bottom_tabs(right_pane)

    def _build_hud(self, parent):
        hud = tk.Frame(parent, bg="#0b0f19", bd=1, relief=tk.SOLID, highlightbackground=BORDER, padx=8, pady=4)
        hud.pack(fill=tk.X, pady=(0, 4))

        self.btn_play = tk.Button(hud, text="▶ PLAY", font=FONT_BOLD, bg="#0284c7", fg="#ffffff", bd=0, padx=8, pady=1, command=self.toggle_play)
        self.btn_play.pack(side=tk.LEFT, padx=2)

        tk.Label(hud, text="SPEED:", font=FONT_BOLD, fg=TEXT_MUTED, bg="#0b0f19").pack(side=tk.LEFT, padx=(10, 2))
        self.btn_spd1 = tk.Button(hud, text="1x", font=FONT_SM, bg="#0284c7", fg="#ffffff", bd=0, padx=4, pady=1, command=lambda: self.set_speed(700, self.btn_spd1))
        self.btn_spd1.pack(side=tk.LEFT, padx=1)
        self.btn_spd2 = tk.Button(hud, text="2x", font=FONT_SM, bg=BG_PANEL, fg=TEXT_MAIN, bd=0, padx=4, pady=1, command=lambda: self.set_speed(350, self.btn_spd2))
        self.btn_spd2.pack(side=tk.LEFT, padx=1)
        self.btn_spd4 = tk.Button(hud, text="4x", font=FONT_SM, bg=BG_PANEL, fg=TEXT_MAIN, bd=0, padx=4, pady=1, command=lambda: self.set_speed(150, self.btn_spd4))
        self.btn_spd4.pack(side=tk.LEFT, padx=1)

        tk.Label(hud, text="TIMELINE:", font=FONT_BOLD, fg=TEXT_MUTED, bg="#0b0f19").pack(side=tk.LEFT, padx=(10, 2))
        self.scale_minute = ttk.Scale(hud, from_=0, to=30, orient=tk.HORIZONTAL, command=self._on_slider)
        self.scale_minute.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.lbl_clock = tk.Label(hud, text="08:00 AM | MIN 0/30", font=FONT_MONO_BOLD, fg=ACCENT_BLUE, bg="#0b0f19")
        self.lbl_clock.pack(side=tk.RIGHT, padx=(6, 0))

    def _build_bottom_tabs(self, parent):
        tab_container = tk.Frame(parent, bg=BG_ROOT)
        tab_container.pack(fill=tk.BOTH, expand=True)

        tab_nav = tk.Frame(tab_container, bg=BG_ROOT)
        tab_nav.pack(fill=tk.X)

        self.tab_pages = {}
        self.tab_buttons = {}

        tabs = [
            ("charts", "TRAFFIC CHARTS"),
            ("table", "TELEMETRY LOG"),
            ("theory", "ACADEMIC THEORY"),
        ]

        for tab_id, label in tabs:
            btn = tk.Button(
                tab_nav,
                text=label,
                font=FONT_BOLD,
                bg="#1a2233" if tab_id == "charts" else "#0b0f19",
                fg=ACCENT_BLUE if tab_id == "charts" else TEXT_MUTED,
                bd=0,
                padx=12,
                pady=4,
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(side=tk.LEFT, padx=(0, 2))
            self.tab_buttons[tab_id] = btn

            page = tk.Frame(tab_container, bg=BG_PANEL, bd=1, relief=tk.SOLID, highlightbackground=BORDER)
            self.tab_pages[tab_id] = page

        self.tab_pages["charts"].pack(fill=tk.BOTH, expand=True)

        chart_frame = self.tab_pages["charts"]
        self.chart_queue = QueueChart(chart_frame)
        self.chart_queue.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 2), pady=4)

        self.chart_inflow = InflowChart(chart_frame)
        self.chart_inflow.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 4), pady=4)

        table_frame = self.tab_pages["table"]
        self.table_view = TelemetryTable(table_frame, on_select_step=self.jump_to_step)
        self.table_view.pack(fill=tk.BOTH, expand=True)

        theory_frame = self.tab_pages["theory"]
        txt_theory = tk.Text(theory_frame, wrap=tk.WORD, font=FONT_MONO, bg=BG_CARD, fg=TEXT_MAIN, bd=0, padx=10, pady=8)
        txt_theory.pack(fill=tk.BOTH, expand=True)

        content = (
            "========================================================================================\n"
            "                 METRO TRANSIT SIMULATOR - MODELING & SIMULATION THEORY                 \n"
            "========================================================================================\n\n"
            "1. LINEAR CONGRUENTIAL METHOD (LCM)\n"
            "----------------------------------------------------------------------------------------\n"
            "Recurrence relation:\n"
            "      X(n+1) = [ a * X(n) + c ] mod m\n\n"
            "  * X(0) : Initial seed state\n"
            "  * a    : Multiplier constant\n"
            "  * c    : Increment constant\n"
            "  * m    : Modulus bound\n\n"
            "Mapping to Commuter Arrivals:\n"
            "  Let R = X(n) / m in [0, 1):\n"
            "  • 0.00 <= R < 0.20  ( 0% - 19% )  -->  0 Passengers\n"
            "  • 0.20 <= R < 0.40  ( 20% - 39% )  -->  1 Passenger\n"
            "  • 0.40 <= R < 0.60  ( 40% - 59% )  -->  2 Passengers\n"
            "  • 0.60 <= R < 0.80  ( 60% - 79% )  -->  3 Passengers\n"
            "  • 0.80 <= R < 1.00  ( 80% - 99% )  -->  4 Passengers\n\n"
            "2. EULER'S PHI FUNCTION φ(n) & THE HULL-DOBELL THEOREM\n"
            "----------------------------------------------------------------------------------------\n"
            "Euler's Phi measures integers 1 <= k <= n coprime to n: φ(n) = count{k : gcd(k, n) == 1}.\n\n"
            "CRITICAL LESSON:\n"
            "  gcd(a, m) = 1 alone DOES NOT guarantee a full period for an LCM generator!\n\n"
            "Hull-Dobell Theorem conditions for full period of length m (c > 0):\n"
            "  1. gcd(c, m) = 1  (c and m are coprime)\n"
            "  2. Every prime factor of m divides (a - 1)\n"
            "  3. If m is divisible by 4, then (a - 1) is divisible by 4\n\n"
            "3. REAL-WORLD TRANSIT APPLICATION\n"
            "----------------------------------------------------------------------------------------\n"
            "Simulates stochastic arrivals at a Philippine jeepney terminal with periodic headway\n"
            "dispatches and seating capacities, tracking bottleneck queue peaks and wait times.\n"
        )
        txt_theory.insert(tk.END, content)
        txt_theory.config(state=tk.DISABLED)

    def switch_tab(self, active_id):
        for tid, page in self.tab_pages.items():
            page.pack_forget()
            btn = self.tab_buttons[tid]
            if tid == active_id:
                btn.config(bg="#1a2233", fg=ACCENT_BLUE)
            else:
                btn.config(bg="#0b0f19", fg=TEXT_MUTED)
        self.tab_pages[active_id].pack(fill=tk.BOTH, expand=True)

    def set_speed(self, delay_ms, active_btn):
        self.play_speed_ms = delay_ms
        for b in (self.btn_spd1, self.btn_spd2, self.btn_spd4):
            b.config(bg=BG_PANEL, fg=TEXT_MAIN)
        active_btn.config(bg="#0284c7", fg="#ffffff")

    def toggle_play(self):
        if self.is_playing:
            self.stop_play()
        else:
            self.start_play()

    def start_play(self):
        if not self.sim_data:
            return
        self.is_playing = True
        self.btn_play.config(text="⏸ PAUSE", bg=ACCENT_AMBER, fg="#0f172a")
        self._tick()

    def stop_play(self):
        self.is_playing = False
        self.btn_play.config(text="▶ PLAY", bg="#0284c7", fg="#ffffff")
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None

    def _tick(self):
        if not self.is_playing:
            return
        dur = self.sim_data["parameters"]["duration"]
        if self.current_minute >= dur:
            self.current_minute = 0
        else:
            self.current_minute += 1
        self.scale_minute.set(self.current_minute)
        self._render_step(self.current_minute)
        self.play_job = self.root.after(self.play_speed_ms, self._tick)

    def step_minute(self, delta):
        self.stop_play()
        if not self.sim_data:
            return
        dur = self.sim_data["parameters"]["duration"]
        new_min = max(0, min(dur, self.current_minute + delta))
        self.scale_minute.set(new_min)
        self._render_step(new_min)

    def jump_to_step(self, minute_idx):
        self.stop_play()
        self.scale_minute.set(minute_idx)
        self._render_step(minute_idx)

    def _on_slider(self, val):
        if not self.sim_data:
            return
        m = int(float(val))
        if m != self.current_minute:
            self._render_step(m)

    def load_preset(self, key):
        p = PRESETS.get(key, PRESETS["default"])
        self.param_panel.set_values(p)
        self.run_sim()

    def run_sim(self):
        self.stop_play()
        try:
            p = self.param_panel.get_values()
        except ValueError:
            messagebox.showerror("Validation Error", "All parameters must be valid integers.")
            return

        if p["m"] <= 0 or p["duration"] <= 0 or p["interval"] <= 0 or p["capacity"] <= 0 or p["seed"] < 0:
            messagebox.showerror("Validation Error", "Parameters must be valid positive values.")
            return

        self.sim_data = run_simulation(
            seed=p["seed"],
            a=p["a"],
            c=p["c"],
            m=p["m"],
            duration=p["duration"],
            jeepney_interval=p["interval"],
            jeepney_capacity=p["capacity"]
        )

        self.scale_minute.config(to=p["duration"])
        self.current_minute = 0
        self.scale_minute.set(0)

        self.kpi_bar.update_kpis(self.sim_data["summary"])
        self.euler_panel.update_audit(
            self.sim_data["parameters"],
            self.sim_data["euler_phi"],
            self.sim_data["hull_dobell"]
        )
        self.table_view.populate(self.sim_data)
        self.chart_queue.render(self.sim_data["steps"])
        self.chart_inflow.render(self.sim_data["steps"])
        self._render_step(0)

    def _render_step(self, minute_idx):
        if not self.sim_data or minute_idx >= len(self.sim_data["steps"]):
            return
        self.current_minute = minute_idx
        step = self.sim_data["steps"][minute_idx]
        dur = self.sim_data["parameters"]["duration"]

        self.lbl_clock.config(text=f"{step['time_str']} AM | MIN {step['minute']}/{dur}")
        self.math_trace.update_trace(step)
        self.traffic_canvas.render(step, self.sim_data["parameters"])
        self.table_view.select_minute(minute_idx)
