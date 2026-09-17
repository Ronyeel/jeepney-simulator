import tkinter as tk
import sys
import time

from simulation import run_simulation, euler_phi
from ui.road_scene import RoadScene
from ui.vehicles import Jeepney, Tricycle, SumoCar
from ui.passengers import Passenger
from ui.results_panel import ResultsPanel
from ui.theme import (
    BG_ROOT, BG_TOOLBAR, TOOLBAR_BORDER, TOOLBAR_FG,
    STATUSBAR_BG, STATUSBAR_FG, PAX_COLORS, CAR_COLORS,
    FONT_MENU, FONT_TOOLBAR, FONT_TOOLBAR_BOLD, FONT_DIGITAL, FONT_STATUS
)

PRESETS = {
    "full_period": {"label": "Full Period Example (a=21, c=3, m=100)",  "seed": 13, "a": 21, "c": 3,  "m": 100, "dur": 30, "int": 5, "cap": 12},
    "suboptimal":  {"label": "Suboptimal Example (a=21, c=5, m=100)",   "seed": 13, "a": 21, "c": 5,  "m": 100, "dur": 30, "int": 5, "cap": 12},
    "rush_hour":   {"label": "Rush Hour Example (a=41, c=3, m=100)",    "seed": 7,  "a": 41, "c": 3,  "m": 100, "dur": 45, "int": 4, "cap": 12},
    "textbook":    {"label": "Textbook Example (a=5, c=3, m=16)",       "seed": 1,  "a": 5,  "c": 3,  "m": 16,  "dur": 20, "int": 4, "cap": 12},
}

_TICKS_PER_MINUTE = 40
_LABEL_UPDATE_EVERY = 4  

class SimulatorWindow:
    TICK_MS = 30  

    def __init__(self, root):
        self.root = root
        self.root.title("Jeepney Passenger Queue Simulation - RR-EL")
        self.root.configure(bg=BG_ROOT)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww = min(1280, int(sw * 0.95))
        wh = min(760, int(sh * 0.92))
        self.root.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")
        self.root.minsize(940, 560)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(400, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

        self.WW = ww
        self.WH = wh

        self.sim_data = None
        self.sim_steps = []
        self.current_minute = 0
        self.is_running = False
        self.delay_ms = self.TICK_MS
        self._tick_job = None
        self._sub_tick = 0
        self._label_tick = 0

        self.jeepney = None
        self.departing_jeepneys = []
        self._is_stepping = False
        self._step_ticks_remaining = 0
        self.traffic_cars = []
        self.tricycles = []
        self.passengers = []
        self.queue_pax = []
        self.spawned_minutes = set()
        self._current_preset = "full_period"

        self._move_debounce = None
        self._last_geom = ""

        self._build_ui()
        self.root.bind("<F2>", lambda e: self._toggle_results())
        self.root.bind("<Configure>", self._on_configure)
        self._init_simulation("full_period")

    def _quit(self):
        self.is_running = False
        if self._tick_job:
            self.root.after_cancel(self._tick_job)
        self.root.destroy()
        sys.exit(0)

    def _build_ui(self):
        self._build_toolbar()
        self._build_statusbar()   
        self._build_results_panel()
        self._build_canvas()

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=BG_TOOLBAR, height=36, bd=0, relief=tk.FLAT)
        bar.pack(side=tk.TOP, fill=tk.X)
        bar.pack_propagate(False)

        def divider(side=tk.LEFT):
            d = tk.Frame(bar, bg=TOOLBAR_BORDER, width=1)
            d.pack(side=side, fill=tk.Y, padx=4, pady=4)

        def tool_btn(text, cmd):
            b = tk.Button(
                bar, text=text, command=cmd,
                bg=BG_TOOLBAR, fg=TOOLBAR_FG,
                activebackground="#e5e5e5", activeforeground="#000000",
                relief=tk.GROOVE, bd=1,
                font=FONT_TOOLBAR_BOLD, padx=6, pady=2, cursor="hand2"
            )
            b.pack(side=tk.LEFT, padx=2, pady=4)
            return b

        self.btn_play = tool_btn("▶  Start", self._toggle_sim)
        tool_btn("⟳  Reload", lambda: self._init_simulation(self._current_preset))
        divider()

        tk.Label(bar, text="Time:", bg=BG_TOOLBAR, fg="#444444", font=FONT_TOOLBAR).pack(side=tk.LEFT, padx=(4, 2))
        time_frame = tk.Frame(bar, bg="#000000", padx=6, pady=2)
        time_frame.pack(side=tk.LEFT, padx=2)
        self.lbl_time = tk.Label(time_frame, text="08:00 (m0)", bg="#000000", fg="#22c55e", font=FONT_DIGITAL)
        self.lbl_time.pack()
        divider()

        self.lbl_phi_hud = tk.Label(
            bar, text="φ(m) = --", bg="#e0f2fe", fg="#0369a1",
            font=FONT_TOOLBAR_BOLD, padx=6, pady=1, relief=tk.GROOVE, bd=1, cursor="hand2"
        )
        self.lbl_phi_hud.pack(side=tk.RIGHT, padx=3)
        self.lbl_phi_hud.bind("<Button-1>", lambda e: self.results_panel._show_phi_calc_dialog() if hasattr(self, 'results_panel') else None)

        self.lbl_lcm = tk.Label(bar, text="LCM: --", bg=BG_TOOLBAR, fg="#334155", font=FONT_TOOLBAR)
        self.lbl_lcm.pack(side=tk.RIGHT, padx=4)

        divider(side=tk.RIGHT)

        tk.Label(bar, text="Delay:", bg=BG_TOOLBAR, fg="#444444", font=FONT_TOOLBAR).pack(side=tk.LEFT, padx=(1, 1))
        self.speed_var = tk.StringVar(value="30")
        speed_menu = tk.OptionMenu(bar, self.speed_var, "10", "20", "30", "50", "100", command=self._on_speed_change)
        speed_menu.config(bg="#ffffff", fg="#000000", relief=tk.GROOVE, bd=1, font=FONT_TOOLBAR, padx=2)
        speed_menu.pack(side=tk.LEFT, padx=1)
        divider()

        tk.Label(bar, text="Preset:", bg=BG_TOOLBAR, fg="#444444", font=FONT_TOOLBAR).pack(side=tk.LEFT, padx=(1, 1))
        self.preset_var = tk.StringVar(value="full_period")
        preset_keys = list(PRESETS.keys())
        preset_menu = tk.OptionMenu(bar, self.preset_var, *preset_keys, command=self._on_preset_change)
        preset_menu.config(bg="#ffffff", fg="#000000", relief=tk.GROOVE, bd=1, font=FONT_TOOLBAR, padx=2)
        preset_menu.pack(side=tk.LEFT, padx=1)
        divider()

        lcm_group = tk.LabelFrame(
            bar, text=" Advanced LCM Parameters ",
            bg=BG_TOOLBAR, fg="#0284c7", font=("Segoe UI", 7, "bold"),
            bd=1, relief=tk.GROOVE, padx=4, pady=0
        )
        lcm_group.pack(side=tk.LEFT, padx=3, pady=1)

        tk.Label(lcm_group, text="X₀:", bg=BG_TOOLBAR, fg="#334155", font=FONT_TOOLBAR_BOLD).pack(side=tk.LEFT, padx=(1, 1))
        self.seed_var = tk.IntVar(value=13)
        seed_spin = tk.Spinbox(
            lcm_group, from_=0, to=99999, increment=1,
            textvariable=self.seed_var, width=4,
            font=FONT_TOOLBAR, relief=tk.GROOVE, bd=1,
            command=self._on_seed_change
        )
        seed_spin.pack(side=tk.LEFT, padx=(0, 2))
        seed_spin.bind("<Return>", lambda e: self._on_seed_change())
        seed_spin.bind("<FocusOut>", lambda e: self._on_seed_change())

        tk.Label(lcm_group, text="a:", bg=BG_TOOLBAR, fg="#334155", font=FONT_TOOLBAR_BOLD).pack(side=tk.LEFT, padx=(2, 1))
        self.a_var = tk.IntVar(value=21)
        a_spin = tk.Spinbox(
            lcm_group, from_=1, to=9999, increment=1,
            textvariable=self.a_var, width=4,
            font=FONT_TOOLBAR, relief=tk.GROOVE, bd=1,
            command=self._on_a_change
        )
        a_spin.pack(side=tk.LEFT, padx=(0, 2))
        a_spin.bind("<Return>", lambda e: self._on_a_change())
        a_spin.bind("<FocusOut>", lambda e: self._on_a_change())

        tk.Label(lcm_group, text="c:", bg=BG_TOOLBAR, fg="#334155", font=FONT_TOOLBAR_BOLD).pack(side=tk.LEFT, padx=(2, 1))
        self.c_var = tk.IntVar(value=3)
        c_spin = tk.Spinbox(
            lcm_group, from_=0, to=9999, increment=1,
            textvariable=self.c_var, width=4,
            font=FONT_TOOLBAR, relief=tk.GROOVE, bd=1,
            command=self._on_c_change
        )
        c_spin.pack(side=tk.LEFT, padx=(0, 2))
        c_spin.bind("<Return>", lambda e: self._on_c_change())
        c_spin.bind("<FocusOut>", lambda e: self._on_c_change())

        tk.Label(lcm_group, text="m:", bg=BG_TOOLBAR, fg="#334155", font=FONT_TOOLBAR_BOLD).pack(side=tk.LEFT, padx=(2, 1))
        self.m_var = tk.IntVar(value=100)
        m_spin = tk.Spinbox(
            lcm_group, from_=2, to=10000, increment=1,
            textvariable=self.m_var, width=5,
            font=FONT_TOOLBAR, relief=tk.GROOVE, bd=1,
            command=self._on_m_change
        )
        m_spin.pack(side=tk.LEFT, padx=(0, 1))
        m_spin.bind("<Return>", lambda e: self._on_m_change())
        m_spin.bind("<FocusOut>", lambda e: self._on_m_change())
        m_spin.bind("<KeyRelease>", self._on_m_key_release)
        divider()

        tk.Label(bar, text="Dur:", bg=BG_TOOLBAR, fg="#444444", font=FONT_TOOLBAR).pack(side=tk.LEFT, padx=(1, 1))
        self.dur_var = tk.IntVar(value=30)
        dur_spin = tk.Spinbox(
            bar, from_=5, to=120, increment=5,
            textvariable=self.dur_var, width=3,
            font=FONT_TOOLBAR, relief=tk.GROOVE, bd=1,
            command=self._on_duration_change
        )
        dur_spin.pack(side=tk.LEFT, padx=(0, 1))
        dur_spin.bind("<Return>", lambda e: self._on_duration_change())
        dur_spin.bind("<FocusOut>", lambda e: self._on_duration_change())
        divider()

        tk.Label(bar, text="Cap:", bg=BG_TOOLBAR, fg="#444444", font=FONT_TOOLBAR).pack(side=tk.LEFT, padx=(1, 1))
        self.cap_var = tk.IntVar(value=12)
        cap_spin = tk.Spinbox(
            bar, from_=4, to=30, increment=2,
            textvariable=self.cap_var, width=3,
            font=FONT_TOOLBAR, relief=tk.GROOVE, bd=1,
            command=self._on_capacity_change
        )
        cap_spin.pack(side=tk.LEFT, padx=(0, 1))
        cap_spin.bind("<Return>", lambda e: self._on_capacity_change())
        cap_spin.bind("<FocusOut>", lambda e: self._on_capacity_change())

    def _build_canvas(self):
        self.canvas = RoadScene(self.root, self.WW, 400)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.draw_environment()

    def _build_results_panel(self):
        self.results_panel = ResultsPanel(self.root)
        self.results_panel.sim_window = self
        self.results_panel.show()  

    def _build_statusbar(self):
        self.lbl_status = tk.Label(self.root)
        self.lbl_stats = tk.Label(self.root)

    def _on_speed_change(self, val):
        self.delay_ms = int(val)

    def _on_preset_change(self, val):
        self.preset_var.set(val)
        self.dur_var.set(PRESETS[val]["dur"])
        self.seed_var.set(PRESETS[val]["seed"])
        self.a_var.set(PRESETS[val]["a"])
        self.c_var.set(PRESETS[val]["c"])
        self.m_var.set(PRESETS[val]["m"])
        self.cap_var.set(PRESETS[val]["cap"])
        self._init_simulation(val)

    def _on_m_key_release(self, event=None):
        try:
            val = int(self.m_var.get())
            if val >= 1:
                res = euler_phi(val)
                self.lbl_phi_hud.config(text=f"φ({val}) = {res}")
        except (ValueError, tk.TclError):
            pass

    def _on_a_change(self):
        try:
            val = int(self.a_var.get())
            if val < 1:
                val = 1
            self.a_var.set(val)
        except (ValueError, tk.TclError):
            self.a_var.set(21)
        self._init_simulation(self._current_preset)

    def _on_c_change(self):
        try:
            val = int(self.c_var.get())
            if val < 0:
                val = 0
            self.c_var.set(val)
        except (ValueError, tk.TclError):
            self.c_var.set(3)
        self._init_simulation(self._current_preset)

    def _on_m_change(self):
        try:
            val = int(self.m_var.get())
            if val < 2:
                val = 2
            elif val > 10000:
                val = 10000
            self.m_var.set(val)
        except (ValueError, tk.TclError):
            self.m_var.set(100)
        self._init_simulation(self._current_preset)

    def _on_seed_change(self):
        try:
            val = int(self.seed_var.get())
            if val < 0:
                val = 0
            self.seed_var.set(val)
        except (ValueError, tk.TclError):
            self.seed_var.set(13)
        self._init_simulation(self._current_preset)

    def _on_capacity_change(self):
        try:
            val = int(self.cap_var.get())
            if val < 4:
                val = 4
            elif val > 30:
                val = 30
            self.cap_var.set(val)
        except (ValueError, tk.TclError):
            self.cap_var.set(12)
        self._init_simulation(self._current_preset)

    def _on_duration_change(self):
        try:
            val = int(self.dur_var.get())
            if val < 5:
                val = 5
            elif val > 120:
                val = 120
            self.dur_var.set(val)
        except (ValueError, tk.TclError):
            self.dur_var.set(30)
        self._init_simulation(self._current_preset)

    def _init_simulation(self, preset_key="full_period"):
        self._current_preset = preset_key
        cfg = PRESETS[preset_key]

        if self._tick_job:
            self.root.after_cancel(self._tick_job)
            self._tick_job = None
        self.is_running = False
        self.btn_play.config(text="▶  Start")

        dur = max(5, min(120, int(self.dur_var.get())))
        try:
            seed = max(0, int(self.seed_var.get()))
        except (ValueError, tk.TclError):
            seed = cfg["seed"]
            self.seed_var.set(seed)

        try:
            a_val = max(1, int(self.a_var.get()))
        except (ValueError, tk.TclError):
            a_val = cfg["a"]
            self.a_var.set(a_val)

        try:
            c_val = max(0, int(self.c_var.get()))
        except (ValueError, tk.TclError):
            c_val = cfg["c"]
            self.c_var.set(c_val)

        try:
            m_val = max(2, min(10000, int(self.m_var.get())))
        except (ValueError, tk.TclError):
            m_val = cfg["m"]
            self.m_var.set(m_val)

        try:
            cap = max(4, min(30, int(self.cap_var.get())))
        except (ValueError, tk.TclError):
            cap = cfg["cap"]
            self.cap_var.set(cap)

        self.sim_data = run_simulation(
            seed=seed, a=a_val, c=c_val, m=m_val,
            duration=dur, jeepney_interval=cfg["int"], jeepney_capacity=cap
        )
        self.sim_steps = self.sim_data["steps"]
        self.current_minute = 0
        self.spawned_minutes = set()
        self._sub_tick = 0
        self._label_tick = 0
        self._step_ticks_remaining = 0
        self._sim_completed = False

        if self.jeepney:
            self.jeepney.destroy()
            self.jeepney = None
        for dj in self.departing_jeepneys:
            dj.destroy()
        self.departing_jeepneys = []
        for pax in self.passengers:
            pax.destroy()
        self.passengers = []
        self.queue_pax = []

        for car in self.traffic_cars:
            car.destroy()
        for tri in self.tricycles:
            tri.destroy()
        self.traffic_cars = []
        self.tricycles = []

        hd = self.sim_data["hull_dobell"]
        phi = self.sim_data["euler_phi"]
        self.lbl_phi_hud.config(
            text=f"φ({m_val}) = {phi['phi_m']}"
        )

        orig_seed = self.sim_data["parameters"]["original_seed"]
        eff_seed  = self.sim_data["parameters"]["seed"]
        is_norm   = self.sim_data["parameters"]["seed_normalized"]
        norm_note = f" [Notice: Seed {orig_seed} mod {m_val} = {eff_seed}]" if is_norm else ""

        self.lbl_lcm.config(text=f"X(n+1)=({a_val}·Xn+{c_val}) mod {m_val}")
        self.lbl_time.config(text="08:00 (m0)")
        self.lbl_status.config(text=f"Ready. Press ▶ Start to begin. Duration: {dur}m, Cap: {cap} pax.{norm_note}")
        self.lbl_stats.config(text="vehicles: 0 | queue: 0 | served: 0 | trip: 0")

        self.canvas.draw_environment()

        self.results_panel.load_sim(self.sim_data)

    def _spawn_ambient_traffic(self):
        for car in self.traffic_cars:
            car.destroy()
        for tri in self.tricycles:
            tri.destroy()

        self.traffic_cars = []
        self.tricycles = []

        W = self.WW
        self.traffic_cars.append(SumoCar(self.canvas, W + 60,  self.canvas.wb_lane_1, 2.8, -1, "#16a34a"))
        self.traffic_cars.append(SumoCar(self.canvas, W + 320, self.canvas.wb_lane_2, 2.4, -1, "#eab308"))

        self.traffic_cars.append(SumoCar(self.canvas, -60,  self.canvas.eb_lane_1, 2.6, 1, "#f97316"))
        self.traffic_cars.append(SumoCar(self.canvas, -340, self.canvas.eb_lane_1, 2.2, 1, "#0284c7"))

        self.tricycles.append(Tricycle(self.canvas, W + 160, self.canvas.wb_lane_2, 1.8, -1))
        self.tricycles.append(Tricycle(self.canvas, -200,    self.canvas.eb_lane_2, 1.9, 1))

    def _start_sim(self):
        if not self.is_running:
            self._toggle_sim()

    def _stop_sim(self):
        if self.is_running:
            self._toggle_sim()

    def _step_once(self):
        if self.is_running or getattr(self, "_is_stepping", False):
            return
        if not self.traffic_cars and not self.tricycles:
            self._spawn_ambient_traffic()

        self._is_stepping = True
        self._step_ticks_remaining = _TICKS_PER_MINUTE
        self._advance_minute()
        self._run_step_animation()

    def _run_step_animation(self):
        if self.is_running:
            self._is_stepping = False
            return
        if getattr(self, "_step_ticks_remaining", 0) > 0:
            self._step_ticks_remaining -= 1
            self._update_step_frame()
            self.root.after(max(4, self.delay_ms // 2), self._run_step_animation)
        else:
            self._is_stepping = False

    def _update_step_frame(self):
        W = max(self.canvas.winfo_width(), getattr(self.canvas, "W", 1280))
        for i, car in enumerate(self.traffic_cars):
            car.update()
            if car.direction == -1 and car.x < -80:
                car.x = W + 80
                car.set_color(CAR_COLORS[(i + self.current_minute) % len(CAR_COLORS)])
            elif car.direction == 1 and car.x > W + 80:
                car.x = -80
                car.set_color(CAR_COLORS[(i + self.current_minute + 2) % len(CAR_COLORS)])

        for tri in self.tricycles:
            tri.update()
            if tri.direction == -1 and tri.x < -80:
                tri.x = W + 80
            elif tri.direction == 1 and tri.x > W + 80:
                tri.x = -80

        for pax in self.passengers:
            pax.update()

        if self.jeepney:
            self.jeepney.update()
            if self.jeepney.state == "waiting":
                target = getattr(self.jeepney, "target_served", self.jeepney.capacity)
                if self.jeepney.passengers_onboard < target and self.queue_pax:
                    boarders = [p for p in self.queue_pax if p.state == "queued"]
                    if boarders:
                        pax = boarders[0]
                        pax.state = "boarding"
                        pax.seat_x = self.jeepney.x
                        pax.seat_y = self.jeepney.y
                        self.queue_pax.remove(pax)
                        self.jeepney.set_occupied(self.jeepney.passengers_onboard + 1)
                loading = any(p.state == "boarding" for p in self.passengers)
                ready_to_leave = (self.jeepney.passengers_onboard >= target or not self.queue_pax) and not loading
                if ready_to_leave:
                    self.jeepney.start_departure()
            elif self.jeepney.state == "departing":
                self.departing_jeepneys.append(self.jeepney)
                self.jeepney = None

        surviving_departing = []
        for dj in self.departing_jeepneys:
            dj.update()
            if dj.state == "done":
                dj.destroy()
            else:
                surviving_departing.append(dj)
        self.departing_jeepneys = surviving_departing

    def _toggle_sim(self):
        if self.is_running:
            self.is_running = False
            self.btn_play.config(text="▶  Start")
            if self._tick_job:
                self.root.after_cancel(self._tick_job)
                self._tick_job = None
        else:
            self.is_running = True
            self.btn_play.config(text="⏸  Pause")
            if not self.traffic_cars and not self.tricycles:
                self._spawn_ambient_traffic()
            self._schedule_tick()

    def _schedule_tick(self):
        if self.is_running:
            self._tick_job = self.root.after(self.delay_ms, self._tick)

    def _on_configure(self, event):
        if event.widget is not self.root:
            return
        geom = self.root.winfo_geometry()
        if geom == self._last_geom:
            return  
        self._last_geom = geom

        if self.is_running and self._tick_job:
            self.root.after_cancel(self._tick_job)
            self._tick_job = None

        if self._move_debounce:
            self.root.after_cancel(self._move_debounce)
        self._move_debounce = self.root.after(150, self._on_drag_settled)

    def _on_drag_settled(self):
        self._move_debounce = None
        if self.is_running and self._tick_job is None:
            self._schedule_tick()

    def _tick(self):
        if not self.is_running:
            return
        t0 = time.perf_counter()
        self._update()
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        if self.is_running:
            delay = max(5, self.delay_ms - elapsed_ms)
            self._tick_job = self.root.after(delay, self._tick)

    def _update(self):
        W = max(self.canvas.winfo_width(), getattr(self.canvas, "W", 1280))

        if getattr(self, "_sim_completed", False):
            if not self.jeepney and not self.departing_jeepneys:
                self.is_running = False
                if self._tick_job:
                    self.root.after_cancel(self._tick_job)
                    self._tick_job = None
                self.btn_play.config(text="▶  Start")
                return

        for i, car in enumerate(self.traffic_cars):
            car.update()
            if car.direction == -1 and car.x < -80:
                car.x = W + 80
                car.set_color(CAR_COLORS[(i + self.current_minute) % len(CAR_COLORS)])
            elif car.direction == 1 and car.x > W + 80:
                car.x = -80
                car.set_color(CAR_COLORS[(i + self.current_minute + 2) % len(CAR_COLORS)])

        for tri in self.tricycles:
            tri.update()
            if tri.direction == -1 and tri.x < -80:
                tri.x = W + 80
            elif tri.direction == 1 and tri.x > W + 80:
                tri.x = -80

        for pax in self.passengers:
            pax.update()

        if self.jeepney:
            self.jeepney.update()

            if self.jeepney.state == "waiting":
                target = getattr(self.jeepney, "target_served", self.jeepney.capacity)
                if self.jeepney.passengers_onboard < target and self.queue_pax:
                    boarders = [p for p in self.queue_pax if p.state == "queued"]
                    if boarders:
                        pax = boarders[0]
                        pax.state = "boarding"
                        pax.seat_x = self.jeepney.x
                        pax.seat_y = self.jeepney.y
                        self.queue_pax.remove(pax)
                        self.jeepney.set_occupied(self.jeepney.passengers_onboard + 1)

                loading = any(p.state == "boarding" for p in self.passengers)
                ready_to_leave = (self.jeepney.passengers_onboard >= target or not self.queue_pax) and not loading
                if ready_to_leave:
                    self.jeepney.start_departure()

            elif self.jeepney.state == "departing":
                self.departing_jeepneys.append(self.jeepney)
                self.jeepney = None

        surviving_departing = []
        for dj in self.departing_jeepneys:
            dj.update()
            if dj.state == "done":
                dj.destroy()
            else:
                surviving_departing.append(dj)
        self.departing_jeepneys = surviving_departing

        self._sub_tick += 1
        if self._sub_tick >= _TICKS_PER_MINUTE:
            self._sub_tick = 0
            self._advance_minute()
        else:
            self._label_tick += 1
            if self._label_tick >= _LABEL_UPDATE_EVERY:
                self._label_tick = 0
                self._update_stats_label()

    def _sync_visual_queue(self, target_queue):
        while len(self.queue_pax) > target_queue:
            pax = self.queue_pax.pop(0)
            pax.destroy()
            if pax in self.passengers:
                self.passengers.remove(pax)

        while len(self.queue_pax) < target_queue:
            q_idx = len(self.queue_pax)
            q_x = self.canvas.bay_x + 10 + (q_idx % 12) * 14
            q_y = self.canvas.road_bot + 14 + (q_idx // 12) * 14
            color = PAX_COLORS[q_idx % len(PAX_COLORS)]
            p = Passenger(self.canvas, q_x, q_y, q_x, q_y, color)
            p.state = "queued"
            self.passengers.append(p)
            self.queue_pax.append(p)

        for q_idx, p in enumerate(self.queue_pax):
            q_x = self.canvas.bay_x + 10 + (q_idx % 12) * 14
            q_y = self.canvas.road_bot + 14 + (q_idx // 12) * 14
            if p.state == "queued":
                p.x = q_x
                p.y = q_y
                if p.item_id:
                    r = p.RADIUS
                    self.canvas.coords(p.item_id, q_x - r, q_y - r, q_x + r, q_y + r)

    def _get_live_stats(self):
        m = self.current_minute
        observed = self.sim_steps[1 : m + 1]
        cum_arrivals = sum(st["arrivals"] for st in observed)
        cum_served   = sum(st["served"] for st in observed)
        cum_trips    = sum(1 for st in observed if st.get("jeepney_arrived"))
        curr_step    = self.sim_steps[min(m, len(self.sim_steps) - 1)]
        curr_queue   = curr_step["queue"]
        return {
            "arrivals": cum_arrivals,
            "served": cum_served,
            "trips": cum_trips,
            "queue": curr_queue,
            "step": curr_step,
        }

    def _advance_minute(self):
        dur = self.sim_data["parameters"]["duration"]
        if self.current_minute >= dur:
            self._sim_completed = True
            s = self.sim_data["summary"]
            self.lbl_status.config(
                text=f"Simulation finished — {s['total_arrivals']} arrived, {s['total_served']} served in {s['jeepneys_dispatched']} trips. Duration {dur}m complete."
            )
            if not self.jeepney and not self.departing_jeepneys:
                self.is_running = False
                if self._tick_job:
                    self.root.after_cancel(self._tick_job)
                    self._tick_job = None
                self.btn_play.config(text="▶  Start")
            return

        self.current_minute += 1
        step = self.sim_steps[min(self.current_minute, len(self.sim_steps) - 1)]

        for i in range(step["arrivals"]):
            q_idx = len(self.queue_pax)
            q_x = self.canvas.bay_x + 10 + (q_idx % 12) * 14
            q_y = self.canvas.road_bot + 14 + (q_idx // 12) * 14
            color = PAX_COLORS[q_idx % len(PAX_COLORS)]
            spawn_x = self.canvas.shed_x + 10 + ((q_idx * 19 + i * 11) % 65)
            spawn_y = self.canvas.shed_y + 10
            p = Passenger(self.canvas, spawn_x, spawn_y, q_x, q_y, color)
            self.passengers.append(p)
            self.queue_pax.append(p)

        if step.get("jeepney_arrived"):
            srv = step["served"]
            cap = self.sim_data["parameters"]["jeepney_capacity"]

            if self.jeepney:
                if self.jeepney.state == "waiting":
                    self.jeepney.start_departure()
                else:
                    self.jeepney.state = "departing"
                self.departing_jeepneys.append(self.jeepney)
                self.jeepney = None

            self.jeepney = Jeepney(
                self.canvas,
                spawn_x=-120,
                lane_y=self.canvas.eb_lane_2,
                bay_x=self.canvas.bay_x + 60,
                bay_y=self.canvas.road_bot - 18,
                capacity=cap
            )
            self.jeepney.target_served = srv

        still_to_board = 0
        if self.jeepney and self.jeepney.state in ("approaching", "docking", "waiting"):
            still_to_board = max(0, self.jeepney.target_served - self.jeepney.passengers_onboard)

        target_visual_queue = step["queue"] + still_to_board
        self._sync_visual_queue(target_visual_queue)

        self._update_labels(step)

    def _update_stats_label(self):
        if not self.sim_data:
            return
        stats = self._get_live_stats()
        active_veh = len(self.traffic_cars) + len(self.tricycles) + (1 if self.jeepney else 0) + len(self.departing_jeepneys)
        self.lbl_stats.config(
            text=f"vehicles: {active_veh} | queue: {stats['queue']} | served: {stats['served']} | trips: {stats['trips']}"
        )

    def _update_labels(self, step):
        t = step["time_str"]
        m = step["minute"]
        stats = self._get_live_stats()

        self.lbl_time.config(text=f"{t} (m{m})")

        lcm_line = step["calculation"].split("\n")[0].strip()
        self.lbl_lcm.config(text=lcm_line[:42])

        active_veh = len(self.traffic_cars) + len(self.tricycles) + (1 if self.jeepney else 0) + len(self.departing_jeepneys)
        self.lbl_stats.config(
            text=f"vehicles: {active_veh} | queue: {stats['queue']} | served: {stats['served']} | trips: {stats['trips']}"
        )

        j_note = f" Jeepney dispatched ({step['served']} boarded)." if step['jeepney_arrived'] else ""
        self.lbl_status.config(
            text=f"Step {m} ({t}): +{step['arrivals']} pax arrived.{j_note} Waiting queue: {stats['queue']}."
        )

        self.root.after_idle(lambda: self.results_panel.sync_step(self.current_minute))

    def _toggle_results(self):
        self.results_panel.toggle()
