import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, sim_data, current_minute=0):
        super().__init__(parent)
        self.title("Simulation Analysis — LCM & Euler's Phi")
        self.geometry("960x620")
        self.minsize(800, 480)
        self.configure(bg="#ececec")
        self.resizable(True, True)

        self.sim_data = sim_data
        self.current_minute = current_minute
        self._last_synced_minute = -1

        self._build_ui()
        self.load_sim(sim_data)

    def load_sim(self, sim_data):
        self.sim_data = sim_data
        self._last_synced_minute = -1
        self._populate_all()

    def sync_step(self, current_minute):
        if not self.sim_data:
            return
        if current_minute == self._last_synced_minute:
            return  
        self._last_synced_minute = current_minute
        self.current_minute = current_minute
        self._sync_kpi_and_cursor()

    def _build_ui(self):
        top_frame = tk.Frame(self, bg="#dedede", bd=1, relief=tk.SOLID, padx=12, pady=8)
        top_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(
            top_frame,
            text="Modeling & Simulation: Linear Congruential Method & Euler's Phi",
            font=("Segoe UI", 10, "bold"),
            fg="#111111", bg="#dedede"
        ).pack(anchor=tk.W)

        tk.Label(
            top_frame,
            text="Passenger Arrival Queueing & Jeepney Dispatch — Daet–Mercedes Corridor, Camarines Norte",
            font=("Segoe UI", 8),
            fg="#444444", bg="#dedede"
        ).pack(anchor=tk.W, pady=(2, 0))

        content = tk.Frame(self, bg="#ececec", padx=8, pady=4)
        content.pack(fill=tk.BOTH, expand=True)

        kpi_frame = tk.LabelFrame(
            content, text="Simulation Summary",
            font=("Segoe UI", 8, "bold"), bg="#ececec", fg="#333333", padx=8, pady=4
        )
        kpi_frame.pack(fill=tk.X, pady=(0, 6))

        self.kpi_labels = {}
        metrics = [
            ("Total Arrivals", "arrivals"),
            ("Total Served", "served"),
            ("Current Queue", "curr_q"),
            ("Peak Queue", "max_q"),
            ("Avg Queue", "avg_q"),
            ("Trips Dispatched", "trips"),
        ]
        for title, key in metrics:
            box = tk.Frame(kpi_frame, bg="#ffffff", bd=1, relief=tk.SOLID, padx=8, pady=4)
            box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
            tk.Label(box, text=title, font=("Segoe UI", 7), fg="#666666", bg="#ffffff").pack(anchor=tk.W)
            lbl = tk.Label(box, text="--", font=("Consolas", 11, "bold"), fg="#111111", bg="#ffffff")
            lbl.pack(anchor=tk.W)
            self.kpi_labels[key] = lbl

        math_frame = tk.Frame(content, bg="#ececec")
        math_frame.pack(fill=tk.X, pady=(0, 6))

        lcm_box = tk.LabelFrame(
            math_frame, text="1. Linear Congruential Method (LCM)",
            font=("Segoe UI", 8, "bold"), bg="#ececec", fg="#333333", padx=8, pady=4
        )
        lcm_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        self.lbl_lcm_formula = tk.Label(
            lcm_box, text="X(n+1) = (a · X(n) + c) mod m",
            font=("Consolas", 8, "bold"), fg="#111111", bg="#ececec"
        )
        self.lbl_lcm_formula.pack(anchor=tk.W)

        self.lbl_lcm_params = tk.Label(
            lcm_box, text="Parameters: a = --, c = --, m = --, Seed X0 = --",
            font=("Segoe UI", 8), fg="#333333", bg="#ececec"
        )
        self.lbl_lcm_params.pack(anchor=tk.W, pady=(2, 0))

        self.lbl_lcm_desc = tk.Label(
            lcm_box, text="U = X / m  →  mapped to [0–4] passenger arrivals per minute",
            font=("Segoe UI", 8), fg="#555555", bg="#ececec"
        )
        self.lbl_lcm_desc.pack(anchor=tk.W)

        phi_box = tk.LabelFrame(
            math_frame, text="2. Euler's Phi & Hull-Dobell Theorem",
            font=("Segoe UI", 8, "bold"), bg="#ececec", fg="#333333", padx=8, pady=4
        )
        phi_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        self.lbl_phi_val = tk.Label(
            phi_box, text="Euler's Totient: φ(m) = --",
            font=("Consolas", 8, "bold"), fg="#111111", bg="#ececec"
        )
        self.lbl_phi_val.pack(anchor=tk.W)

        self.lbl_c1 = tk.Label(phi_box, text="Condition 1 [gcd(c,m)=1]: --",
                                font=("Segoe UI", 8), fg="#333333", bg="#ececec")
        self.lbl_c1.pack(anchor=tk.W)

        self.lbl_c2 = tk.Label(phi_box, text="Condition 2 [primes divide a-1]: --",
                                font=("Segoe UI", 8), fg="#333333", bg="#ececec")
        self.lbl_c2.pack(anchor=tk.W)

        self.lbl_c3 = tk.Label(phi_box, text="Condition 3 [4|m => 4|(a-1)]: --",
                                font=("Segoe UI", 8), fg="#333333", bg="#ececec")
        self.lbl_c3.pack(anchor=tk.W)

        table_box = tk.LabelFrame(
            content, text="Simulation Log",
            font=("Segoe UI", 8, "bold"), bg="#ececec", fg="#333333", padx=6, pady=4
        )
        table_box.pack(fill=tk.BOTH, expand=True)

        cols = ("step", "time", "curr_x", "calc", "next_x", "u_val",
                "arr", "q_before", "jeep", "srv", "q_rem")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings", height=9)

        headers = [
            ("step",     "n",                  40),
            ("time",     "Time",               55),
            ("curr_x",   "X(n)",               55),
            ("calc",     "(a·Xn+c) mod m",    155),
            ("next_x",   "X(n+1)",             55),
            ("u_val",    "U(0,1)",             60),
            ("arr",      "Arrivals",           60),
            ("q_before", "Queue In",           65),
            ("jeep",     "Jeepney",            65),
            ("srv",      "Served",             55),
            ("q_rem",    "Queue Out",          65),
        ]
        for cid, cname, width in headers:
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=width, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(table_box, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        bottom = tk.Frame(self, bg="#dedede", bd=1, relief=tk.SOLID, padx=8, pady=6)
        bottom.pack(fill=tk.X, padx=8, pady=(4, 8))

        self.lbl_current_step = tk.Label(
            bottom, text="Live status: ready",
            font=("Segoe UI", 8), fg="#333333", bg="#dedede"
        )
        self.lbl_current_step.pack(side=tk.LEFT, padx=4)

        tk.Button(
            bottom, text="Close",
            font=("Segoe UI", 8), bg="#ffffff", fg="#222222",
            relief=tk.GROOVE, bd=1, padx=12, pady=2,
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            bottom, text="Export CSV...",
            font=("Segoe UI", 8), bg="#ffffff", fg="#222222",
            relief=tk.GROOVE, bd=1, padx=10, pady=2,
            command=self._export_csv
        ).pack(side=tk.RIGHT, padx=4)

    def _populate_all(self):
        if not self.sim_data:
            return

        cfg = self.sim_data["parameters"]
        s   = self.sim_data["summary"]
        phi = self.sim_data["euler_phi"]
        hd  = self.sim_data["hull_dobell"]

        self.lbl_lcm_params.config(
            text=f"Parameters: a = {cfg['multiplier']}, c = {cfg['increment']}, m = {cfg['modulus']}, Seed X0 = {cfg['seed']}"
        )

        primes_str = ", ".join(str(f) for f in hd["prime_factors_m"]) or "None"
        self.lbl_phi_val.config(
            text=f"φ({cfg['modulus']}) = {phi['phi_m']} coprimes  |  Prime factors of m: {{{primes_str}}}"
        )

        c1_str = (
            f"✓ gcd({cfg['increment']}, {cfg['modulus']}) = 1"
            if hd["condition1"] else f"✗ gcd ≠ 1"
        )
        self.lbl_c1.config(text=f"Cond 1: {c1_str}")

        c2_str = (
            f"✓ factors {{{primes_str}}} divide a−1 = {cfg['multiplier']-1}"
            if hd["condition2"] else "✗ some prime factor does not divide a−1"
        )
        self.lbl_c2.config(text=f"Cond 2: {c2_str}")

        if cfg["modulus"] % 4 == 0:
            c3_str = (
                f"✓ 4 | m and 4 | a−1 = {cfg['multiplier']-1}"
                if hd["condition3"] else "✗ 4|m but 4 ∤ a−1"
            )
        else:
            c3_str = "✓ m not divisible by 4"
        self.lbl_c3.config(text=f"Cond 3: {c3_str}")

        self.tree.delete(*self.tree.get_children())

        m_val = cfg["modulus"]
        rows = []
        for step in self.sim_data["steps"]:
            n = step["minute"]
            t_str = step["time_str"]
            curr_x = step["current_x"]
            next_x = step["next_x"]

            if n == 0:
                calc_str = f"Seed X0 = {curr_x}"
                u_str = f"{curr_x / m_val:.4f}"
                next_x_str = str(curr_x)
            else:
                a_val = cfg["multiplier"]
                c_val = cfg["increment"]
                calc_str = f"({a_val}·{curr_x}+{c_val}) mod {m_val}"
                u_str = f"{next_x / m_val:.4f}"
                next_x_str = str(next_x)

            arr_str = f"+{step['arrivals']}" if n > 0 else "--"
            j_str  = "Yes" if step["jeepney_arrived"] else "--"
            srv_str = str(step["served"]) if step["jeepney_arrived"] else "--"

            rows.append((
                str(n),  
                (n, t_str, curr_x, calc_str, next_x_str, u_str,
                 arr_str, step["queue_before_jeep"], j_str, srv_str, step["queue"])
            ))

        for iid, values in rows:
            self.tree.insert("", tk.END, iid=iid, values=values)

        self._sync_kpi_and_cursor()

    def _sync_kpi_and_cursor(self):
        if not self.sim_data:
            return

        steps = self.sim_data["steps"]
        step_idx = min(self.current_minute, len(steps) - 1)
        cur_step = steps[step_idx]
        s = self.sim_data["summary"]

        self.kpi_labels["arrivals"].config(text=str(s["total_arrivals"]))
        self.kpi_labels["served"].config(text=str(s["total_served"]))
        self.kpi_labels["curr_q"].config(text=str(cur_step["queue"]))
        self.kpi_labels["max_q"].config(text=str(s["max_queue"]))
        self.kpi_labels["avg_q"].config(text=f"{s['avg_queue']:.2f}")
        self.kpi_labels["trips"].config(text=str(s["jeepneys_dispatched"]))

        dur = self.sim_data["parameters"]["duration"]
        self.lbl_current_step.config(
            text=f"Minute {self.current_minute}/{dur}  ({cur_step['time_str']})  —  Queue: {cur_step['queue']} pax"
        )

        item_id = str(self.current_minute)
        if self.tree.exists(item_id):
            self.tree.selection_set(item_id)
            self.tree.see(item_id)

    def _export_csv(self):
        if not self.sim_data:
            return

        filepath = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"simulation_lcm_{self.sim_data['parameters']['duration']}m.csv"
        )
        if not filepath:
            return

        try:
            cfg = self.sim_data["parameters"]
            m_val = cfg["modulus"]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# Modeling & Simulation: Linear Congruential Method & Euler's Phi\n")
                f.write(f"# Parameters: a={cfg['multiplier']}, c={cfg['increment']}, m={m_val}, seed={cfg['seed']}\n")
                f.write(f"# Euler Totient phi(m): {self.sim_data['euler_phi']['phi_m']}\n")
                f.write(f"# Hull-Dobell Satisfied: {self.sim_data['hull_dobell']['satisfied']}\n\n")
                f.write("Step_n,Time,X_n,Calculation,X_next,U_val,Arrivals,Queue_before,Jeepney,Served,Queue_remaining\n")

                for step in self.sim_data["steps"]:
                    n = step["minute"]
                    curr_x = step["current_x"]
                    next_x = step["next_x"] if step["next_x"] is not None else curr_x
                    u_val = round(next_x / m_val, 4)
                    j = "YES" if step["jeepney_arrived"] else "NO"
                    calc = (
                        f"({cfg['multiplier']}*{curr_x}+{cfg['increment']}) mod {m_val}"
                        if n > 0 else "Seed"
                    )
                    f.write(
                        f"{n},{step['time_str']},{curr_x},\"{calc}\","
                        f"{next_x},{u_val},{step['arrivals']},"
                        f"{step['queue_before_jeep']},{j},{step['served']},{step['queue']}\n"
                    )

            messagebox.showinfo("Export Successful", f"Saved to:\n{filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Export Error", str(e), parent=self)
