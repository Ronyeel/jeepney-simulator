import tkinter as tk
from ui.theme import (
    BG_PANEL,
    BG_CARD,
    BORDER,
    TEXT_MAIN,
    TEXT_MUTED,
    ACCENT_BLUE,
    ACCENT_AMBER,
    ACCENT_GREEN,
    ACCENT_RED,
    FONT_TITLE,
    FONT_BOLD,
    FONT_REG,
    FONT_MONO,
    FONT_MONO_BOLD,
    FONT_SM,
    FONT_XS,
)

class ParametersPanel(tk.LabelFrame):
    def __init__(self, parent, on_run, on_reset):
        super().__init__(
            parent,
            text="  SCENARIO PARAMETERS  ",
            font=FONT_BOLD,
            fg=ACCENT_BLUE,
            bg=BG_PANEL,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=BORDER,
            padx=10,
            pady=8
        )
        self.on_run = on_run
        self.on_reset = on_reset

        self.var_seed = tk.StringVar(value="13")
        self.var_a = tk.StringVar(value="21")
        self.var_c = tk.StringVar(value="5")
        self.var_m = tk.StringVar(value="100")
        self.var_duration = tk.StringVar(value="30")
        self.var_interval = tk.StringVar(value="5")
        self.var_capacity = tk.StringVar(value="8")

        fields = [
            ("Seed X0:", self.var_seed),
            ("Multiplier a:", self.var_a),
            ("Increment c:", self.var_c),
            ("Modulus m:", self.var_m),
            ("Duration (mins):", self.var_duration),
            ("Jeepney Headway:", self.var_interval),
            ("Vehicle Capacity:", self.var_capacity),
        ]

        for r, (label, var) in enumerate(fields):
            lbl = tk.Label(self, text=label, font=FONT_SM, fg=TEXT_MAIN, bg=BG_PANEL)
            lbl.grid(row=r, column=0, sticky=tk.W, pady=2)

            ent = tk.Entry(
                self,
                textvariable=var,
                width=11,
                font=FONT_MONO,
                bg="#0f172a",
                fg=ACCENT_BLUE,
                insertbackground=ACCENT_BLUE,
                bd=1,
                relief=tk.SOLID
            )
            ent.grid(row=r, column=1, sticky=tk.E, pady=2)

        btn_box = tk.Frame(self, bg=BG_PANEL, pady=6)
        btn_box.grid(row=len(fields), column=0, columnspan=2, sticky=tk.EW)

        self.btn_run = tk.Button(
            btn_box,
            text="▶ RUN SIMULATION",
            font=FONT_BOLD,
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=4,
            command=self.on_run
        )
        self.btn_run.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_reset = tk.Button(
            btn_box,
            text="RESET",
            font=FONT_SM,
            bg="#334155",
            fg=TEXT_MAIN,
            relief=tk.FLAT,
            bd=0,
            padx=6,
            pady=4,
            command=self.on_reset
        )
        self.btn_reset.pack(side=tk.LEFT)

    def get_values(self):
        return {
            "seed": int(self.var_seed.get()),
            "a": int(self.var_a.get()),
            "c": int(self.var_c.get()),
            "m": int(self.var_m.get()),
            "duration": int(self.var_duration.get()),
            "interval": int(self.var_interval.get()),
            "capacity": int(self.var_capacity.get()),
        }

    def set_values(self, p):
        self.var_seed.set(str(p["seed"]))
        self.var_a.set(str(p["a"]))
        self.var_c.set(str(p["c"]))
        self.var_m.set(str(p["m"]))
        self.var_duration.set(str(p["dur"]))
        self.var_interval.set(str(p["int"]))
        self.var_capacity.set(str(p["cap"]))

class EulerAuditPanel(tk.LabelFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            text="  EULER'S PHI & HULL-DOBELL AUDIT  ",
            font=FONT_BOLD,
            fg=ACCENT_BLUE,
            bg=BG_PANEL,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=BORDER,
            padx=10,
            pady=8
        )

        self.lbl_phi = tk.Label(self, text="φ(m) = --", font=FONT_TITLE, fg=ACCENT_BLUE, bg=BG_PANEL)
        self.lbl_phi.pack(anchor=tk.W, pady=(0, 2))

        self.lbl_gcd_am = tk.Label(self, text="gcd(a, m) = --", font=FONT_MONO, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_gcd_am.pack(anchor=tk.W, pady=1)

        self.lbl_gcd_cm = tk.Label(self, text="gcd(c, m) = --", font=FONT_MONO, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_gcd_cm.pack(anchor=tk.W, pady=1)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill=tk.X, pady=6)

        tk.Label(self, text="Hull-Dobell Full Period Conditions:", font=FONT_BOLD, fg=TEXT_MAIN, bg=BG_PANEL).pack(anchor=tk.W)

        self.lbl_c1 = tk.Label(self, text="1. gcd(c, m) == 1: --", font=FONT_SM, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_c1.pack(anchor=tk.W, pady=1)

        self.lbl_c2 = tk.Label(self, text="2. Prime factors divide (a - 1): --", font=FONT_SM, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_c2.pack(anchor=tk.W, pady=1)

        self.lbl_c3 = tk.Label(self, text="3. If 4 | m then 4 | (a - 1): --", font=FONT_SM, fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_c3.pack(anchor=tk.W, pady=1)

        self.lbl_status = tk.Label(self, text="Periodicity: --", font=FONT_BOLD, fg=TEXT_MAIN, bg=BG_PANEL)
        self.lbl_status.pack(anchor=tk.W, pady=(6, 2))

        self.lbl_explanation = tk.Label(self, text="", font=FONT_SM, fg=TEXT_MUTED, bg=BG_PANEL, wraplength=260, justify=tk.LEFT)
        self.lbl_explanation.pack(anchor=tk.W, pady=2)

    def update_audit(self, params, phi, hd):
        self.lbl_phi.config(text=f"φ({params['modulus']}) = {phi['phi_m']}")

        a_pass = (phi["gcd_am"] == 1)
        self.lbl_gcd_am.config(
            text=f"gcd(a, m) = gcd({params['multiplier']}, {params['modulus']}) = {phi['gcd_am']} {'[PASS]' if a_pass else '[FAIL]'}",
            fg=ACCENT_GREEN if a_pass else ACCENT_RED
        )

        c_pass = (phi["gcd_cm"] == 1)
        self.lbl_gcd_cm.config(
            text=f"gcd(c, m) = gcd({params['increment']}, {params['modulus']}) = {phi['gcd_cm']} {'[PASS]' if c_pass else '[FAIL]'}",
            fg=ACCENT_GREEN if c_pass else ACCENT_RED
        )

        self.lbl_c1.config(
            text=f"1. gcd(c, m) == 1: {'[PASS]' if hd['condition1'] else '[FAIL]'}",
            fg=ACCENT_GREEN if hd["condition1"] else ACCENT_RED
        )
        self.lbl_c2.config(
            text=f"2. Prime factors divide (a - 1): {'[PASS]' if hd['condition2'] else '[FAIL]'}",
            fg=ACCENT_GREEN if hd["condition2"] else ACCENT_RED
        )
        self.lbl_c3.config(
            text=f"3. If 4 | m then 4 | (a - 1): {'[PASS]' if hd['condition3'] else '[FAIL]'}",
            fg=ACCENT_GREEN if hd["condition3"] else ACCENT_RED
        )

        if hd["satisfied"]:
            self.lbl_status.config(text="Periodicity: FULL PERIOD m [PASS]", fg=ACCENT_GREEN)
            self.lbl_explanation.config(
                text=f"Hull-Dobell satisfied. PRNG generates all {params['modulus']} distinct values before repeating."
            )
        else:
            self.lbl_status.config(text="Periodicity: SUBOPTIMAL CYCLE [FAIL]", fg=ACCENT_RED)
            reasons = []
            if not hd["condition1"]:
                reasons.append(f"gcd(c,m)={phi['gcd_cm']}!=1")
            if not hd["condition2"]:
                reasons.append("Prime factors do not divide (a-1)")
            if not hd["condition3"]:
                reasons.append("4 does not divide (a-1)")
            self.lbl_explanation.config(
                text=f"Violation: {', '.join(reasons)}. Sequence repeats early."
            )

class KpiBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_PANEL)
        self.labels = {}

        cards = [
            ("arrivals", "TOTAL DEMAND", ACCENT_BLUE),
            ("served", "SERVED", ACCENT_GREEN),
            ("remaining", "ACTIVE QUEUE", ACCENT_AMBER),
            ("max_q", "PEAK QUEUE", ACCENT_RED),
            ("avg_q", "AVG QUEUE", "#a855f7"),
            ("jeepneys", "DISPATCHES", "#06b6d4"),
        ]

        for key, title, clr in cards:
            box = tk.Frame(self, bg=BG_CARD, bd=1, relief=tk.SOLID, highlightbackground=BORDER, padx=6, pady=3)
            box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)

            t_lbl = tk.Label(box, text=title, font=FONT_XS, fg=TEXT_MUTED, bg=BG_CARD)
            t_lbl.pack(anchor=tk.CENTER)

            v_lbl = tk.Label(box, text="--", font=FONT_TITLE, fg=clr, bg=BG_CARD)
            v_lbl.pack(anchor=tk.CENTER)
            self.labels[key] = v_lbl

    def update_kpis(self, summary):
        self.labels["arrivals"].config(text=str(summary["total_arrivals"]))
        self.labels["served"].config(text=str(summary["total_served"]))
        self.labels["remaining"].config(text=str(summary["remaining_queue"]))
        self.labels["max_q"].config(text=str(summary["max_queue"]))
        self.labels["avg_q"].config(text=str(summary["avg_queue"]))
        self.labels["jeepneys"].config(text=str(summary["jeepneys_dispatched"]))

class MathTracePanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_PANEL, bd=1, relief=tk.SOLID, highlightbackground=BORDER, padx=8, pady=4)

        top_row = tk.Frame(self, bg=BG_PANEL)
        top_row.pack(fill=tk.X)

        tk.Label(top_row, text="LCM TRACE:", font=FONT_BOLD, fg=ACCENT_BLUE, bg=BG_PANEL).pack(side=tk.LEFT, padx=(0, 8))

        self.lbl_curr = tk.Label(top_row, text="X(n): --", font=FONT_MONO, fg=TEXT_MAIN, bg=BG_PANEL)
        self.lbl_curr.pack(side=tk.LEFT, padx=(0, 12))

        self.lbl_next = tk.Label(top_row, text="X(n+1): --", font=FONT_MONO_BOLD, fg=ACCENT_BLUE, bg=BG_PANEL)
        self.lbl_next.pack(side=tk.LEFT, padx=(0, 12))

        self.lbl_val = tk.Label(top_row, text="LCM Mod: --", font=FONT_MONO, fg=TEXT_MAIN, bg=BG_PANEL)
        self.lbl_val.pack(side=tk.LEFT, padx=(0, 12))

        self.lbl_inflow = tk.Label(top_row, text="Inflow: --", font=FONT_MONO_BOLD, fg=ACCENT_AMBER, bg=BG_PANEL)
        self.lbl_inflow.pack(side=tk.LEFT)

        self.lbl_calc = tk.Label(self, text="X(n+1) = (a * X(n) + c) mod m", font=FONT_XS, fg="#cbd5e1", bg=BG_PANEL)
        self.lbl_calc.pack(anchor=tk.W, pady=(2, 0))

    def update_trace(self, step):
        self.lbl_curr.config(text=f"X(n): {step['current_x']}")
        nxt = str(step["next_x"]) if step["minute"] > 0 else "--"
        self.lbl_next.config(text=f"X(n+1): {nxt}")
        val = str(step["lcm_value"]) if step["minute"] > 0 else "--"
        self.lbl_val.config(text=f"LCM Mod: {val}")
        self.lbl_inflow.config(text=f"Inflow: +{step['arrivals']} pax")

        if step["minute"] == 0:
            self.lbl_calc.config(text=f"Minute 0: Initial Seed X0 = {step['current_x']}. Arrivals begin at Minute 1.")
        else:
            lines = step["calculation"].split("\n")
            one_line = " | ".join([line.strip() for line in lines if line.strip()])
            self.lbl_calc.config(text=one_line)
