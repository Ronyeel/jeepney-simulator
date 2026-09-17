import tkinter as tk
from tkinter import ttk
from simulation import arrival_band_label, euler_phi, euler_phi_breakdown, get_coprimes_list, gcd

class ResultsPanel(tk.Frame):

    PANEL_H = 340  

    def __init__(self, parent):
        super().__init__(parent, bg="#ececec", bd=0, relief=tk.FLAT)

        self.sim_data = None
        self.current_minute = 0
        self._last_synced_minute = -1
        self._visible = False

        self._build_ui()

    def is_visible(self):
        return self._visible

    def show(self):
        self._visible = True
        self.pack(side=tk.BOTTOM, fill=tk.X)
        self.config(height=self.PANEL_H)
        if self.sim_data:
            self._sync_kpi_and_cursor()

    def hide(self):
        self._visible = False
        self.pack_forget()

    def toggle(self):
        if self._visible:
            self.hide()
        else:
            self.show()

    def load_sim(self, sim_data):
        self.sim_data = sim_data
        self.current_minute = 0
        self._last_synced_minute = 0
        self._populate_all()

    def sync_step(self, current_minute):
        if not self.sim_data or not self._visible:
            return
        if current_minute == self._last_synced_minute:
            return

        if current_minute < self._last_synced_minute or self._last_synced_minute < 0:
            self.tree.delete(*self.tree.get_children())
            start_m = 0
        else:
            start_m = self._last_synced_minute + 1

        for m in range(start_m, current_minute + 1):
            self._insert_row_for_step(m)

        self._last_synced_minute = current_minute
        self.current_minute = current_minute
        self._sync_kpi_and_cursor()

    def _build_ui(self):
        tk.Frame(self, bg="#b0b0b0", height=1).pack(fill=tk.X)

        hdr = tk.Frame(self, bg="#d8d8d8", padx=8, pady=3)
        hdr.pack(fill=tk.X)

        tk.Label(
            hdr,
            text="Modeling & Simulation Analysis — LCM & Euler's Phi",
            font=("Segoe UI", 8, "bold"), fg="#111111", bg="#d8d8d8"
        ).pack(side=tk.LEFT)

        content = tk.Frame(self, bg="#ececec")
        content.pack(fill=tk.BOTH, expand=True, padx=6, pady=(3, 2))

        left = tk.Frame(content, bg="#ececec", width=420)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        kpi_frame = tk.LabelFrame(
            left, text="Simulation Statistics", font=("Segoe UI", 7, "bold"),
            bg="#ececec", fg="#1e293b", padx=4, pady=2
        )
        kpi_frame.pack(fill=tk.X, pady=(0, 2))

        self.kpi_labels = {}

        row1 = tk.Frame(kpi_frame, bg="#ececec")
        row1.pack(fill=tk.X, pady=(0, 2))

        primary_metrics = [
            ("Arrivals", "arrivals"),
            ("Served", "served"),
            ("In Queue", "curr_q"),
            ("Peak Q", "max_q"),
            ("Avg Queue", "avg_q"),
        ]
        for title, key in primary_metrics:
            card = tk.Frame(row1, bg="#ffffff", padx=3, pady=2, highlightbackground="#cbd5e1", highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1)
            tk.Label(card, text=title, font=("Segoe UI", 6, "bold"), fg="#64748b", bg="#ffffff").pack(anchor=tk.CENTER)
            lbl = tk.Label(card, text="--", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#ffffff")
            lbl.pack(anchor=tk.CENTER)
            self.kpi_labels[key] = lbl

        for k in ("trips", "arr_rate", "srv_pct", "reconciled", "srv_trip"):
            self.kpi_labels[k] = tk.Label(self)

        lcm_box = tk.LabelFrame(
            left, text="Linear Congruential Method (LCM) & Arrivals",
            font=("Segoe UI", 7, "bold"), bg="#ececec", fg="#1e293b", padx=5, pady=2
        )
        lcm_box.pack(fill=tk.X, pady=(0, 2))

        self.lbl_lcm_formula = tk.Label(
            lcm_box, text="X(n+1) = (a · X(n) + c) mod m",
            font=("Consolas", 8, "bold"), fg="#0284c7", bg="#ececec"
        )
        self.lbl_lcm_formula.pack(anchor=tk.W)

        self.lbl_lcm_params = tk.Label(
            lcm_box, text="a = --   c = --   m = --   X0 = --",
            font=("Segoe UI", 7, "bold"), fg="#334155", bg="#ececec"
        )
        self.lbl_lcm_params.pack(anchor=tk.W, pady=(0, 1))

        map_strip = tk.Frame(lcm_box, bg="#ececec")
        map_strip.pack(fill=tk.X, pady=(1, 1))

        bands = [
            ("U < 0.20", "0 pax"),
            ("0.20–0.50", "1 pax"),
            ("0.50–0.80", "2 pax"),
            ("≥ 0.80", "3 pax"),
        ]
        for prob_txt, pax_txt in bands:
            pill = tk.Frame(map_strip, bg="#ffffff", padx=2, pady=1, highlightbackground="#cbd5e1", highlightthickness=1)
            pill.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
            tk.Label(pill, text=prob_txt, font=("Segoe UI", 6), fg="#64748b", bg="#ffffff").pack()
            tk.Label(pill, text=pax_txt, font=("Segoe UI", 7, "bold"), fg="#0f172a", bg="#ffffff").pack()

        self.lbl_lcm_map1 = tk.Label(lcm_box)
        self.lbl_lcm_map2 = tk.Label(lcm_box)

        self.lbl_phi_val  = tk.Label(self)
        self.lbl_phi_desc = tk.Label(self)
        self.btn_coprimes = tk.Button(self)
        self.btn_phi_calc = tk.Button(self)
        self.lbl_c1       = tk.Label(self)
        self.lbl_c2       = tk.Label(self)
        self.lbl_c3       = tk.Label(self)
        self.lbl_hd_res   = tk.Label(self)

        right = tk.Frame(content, bg="#ececec")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        table_box = tk.LabelFrame(
            right, text=" Simulation Log",
            font=("Segoe UI", 7, "bold"), bg="#ececec", fg="#333333", padx=3, pady=2
        )
        table_box.pack(fill=tk.BOTH, expand=True)

        cols = ("step", "time", "curr_x", "calc", "next_x",
                "u_val", "arr", "q_before", "jeep", "srv", "q_rem")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings", height=7)

        headers = [
            ("step",     "n",               32),
            ("time",     "Time",            48),
            ("curr_x",   "X(n)",            45),
            ("calc",     "(a·Xn+c) mod m", 145),
            ("next_x",   "X(n+1)",          48),
            ("u_val",    "U(0,1)",          55),
            ("arr",      "Arrivals",        52),
            ("q_before", "Queue In",        56),
            ("jeep",     "Jeepney",         54),
            ("srv",      "Served",          48),
            ("q_rem",    "Queue Out",       56),
        ]
        for cid, cname, w in headers:
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=w, anchor=tk.CENTER, minwidth=w)

        vsb = ttk.Scrollbar(table_box, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        self.lbl_current_step = tk.Label(self)

    def _populate_all(self):
        if not self.sim_data:
            return

        cfg = self.sim_data["parameters"]
        phi = self.sim_data["euler_phi"]
        hd  = self.sim_data["hull_dobell"]

        seed_txt = f"X0 = {cfg['seed']}"
        if cfg.get("seed_normalized"):
            seed_txt += f" (mod {cfg['modulus']} from {cfg['original_seed']})"

        self.lbl_lcm_params.config(
            text=f"a = {cfg['multiplier']}   c = {cfg['increment']}   m = {cfg['modulus']}   {seed_txt}"
        )

        primes_str = ", ".join(str(f) for f in hd["prime_factors_m"]) or "None"
        fact_str = phi.get("factorization_str", f"{cfg['modulus']}")

        self.lbl_phi_val.config(
            text=f"φ({cfg['modulus']}) = {phi['phi_m']} coprimes   |   m primes: {{{primes_str}}}"
        )
        self.lbl_phi_desc.config(
            text=f"Euler's Phi: {phi['phi_m']} integers ≤ {cfg['modulus']} are coprime to {cfg['modulus']} ({fact_str})."
        )

        c1ok = hd["condition1"]
        c2ok = hd["condition2"]
        c3ok = hd["condition3"]

        self.lbl_c1.config(
            text=f"Cond 1: {'✓' if c1ok else '✗'} gcd({cfg['increment']},{cfg['modulus']})={'1' if c1ok else phi['gcd_cm']}",
            fg="#15803d" if c1ok else "#dc2626"
        )
        self.lbl_c2.config(
            text=f"Cond 2: {'✓' if c2ok else '✗'} primes {{{primes_str}}} | a−1",
            fg="#15803d" if c2ok else "#dc2626"
        )
        if cfg["modulus"] % 4 == 0:
            c3_text = f"Cond 3: {'✓' if c3ok else '✗'} 4|m & {'4|' if c3ok else '4∤'}a−1"
        else:
            c3_text = "Cond 3: ✓ 4 ∤ m"
            c3ok = True
        self.lbl_c3.config(text=c3_text, fg="#15803d" if c3ok else "#dc2626")

        if hd["satisfied"]:
            self.lbl_hd_res.config(
                text="Status: ✓ FULL PERIOD",
                fg="#15803d"
            )
        else:
            self.lbl_hd_res.config(
                text="Status: ✗ SUBOPTIMAL",
                fg="#dc2626"
            )

        self.tree.delete(*self.tree.get_children())
        for n in range(self.current_minute + 1):
            self._insert_row_for_step(n)

        self._sync_kpi_and_cursor()

    def _format_row_values(self, step):
        cfg = self.sim_data["parameters"]
        m_val = cfg["modulus"]
        n = step["minute"]
        curr_x = step["current_x"]
        next_x = step["next_x"]
        if n == 0:
            calc_str = f"Seed X0 = {curr_x}"
            u_str = f"{curr_x / m_val:.4f}"
            next_x_str = str(curr_x)
        else:
            calc_str = f"({cfg['multiplier']}·{curr_x}+{cfg['increment']}) mod {m_val}"
            u_str = f"{next_x / m_val:.4f}"
            next_x_str = str(next_x)

        return (
            n, step["time_str"], curr_x, calc_str, next_x_str, u_str,
            f"+{step['arrivals']}" if n > 0 else "--",
            step["queue_before_jeep"],
            "Yes" if step["jeepney_arrived"] else "--",
            str(step["served"]) if step["jeepney_arrived"] else "--",
            step["queue"]
        )

    def _insert_row_for_step(self, n):
        iid = str(n)
        if not self.tree.exists(iid):
            steps = self.sim_data["steps"]
            if 0 <= n < len(steps):
                values = self._format_row_values(steps[n])
                self.tree.insert("", tk.END, iid=iid, values=values)

    def _sync_kpi_and_cursor(self):
        if not self.sim_data:
            return
        steps = self.sim_data["steps"]
        k = min(self.current_minute, len(steps) - 1)
        cur = steps[k]

        observed_steps = steps[1:k + 1]
        arrivals_so_far = sum(st["arrivals"] for st in observed_steps)
        served_so_far = sum(st["served"] for st in observed_steps)
        curr_q = cur["queue"]
        max_q = max((st["queue"] for st in steps[0:k + 1]), default=0)
        trips_so_far = sum(1 for st in observed_steps if st.get("jeepney_arrived"))
        avg_q = round(sum(st["queue"] for st in observed_steps) / k, 2) if k > 0 else 0.0
        arr_rate = round(arrivals_so_far / k, 2) if k > 0 else 0.0
        srv_trip = round(served_so_far / trips_so_far, 1) if trips_so_far > 0 else 0.0
        srv_pct = round(served_so_far / arrivals_so_far * 100, 1) if arrivals_so_far > 0 else 0.0

        self.kpi_labels["arrivals"].config(text=str(arrivals_so_far))
        self.kpi_labels["served"].config(text=str(served_so_far))
        self.kpi_labels["curr_q"].config(text=str(curr_q))
        self.kpi_labels["max_q"].config(text=str(max_q))
        self.kpi_labels["trips"].config(text=str(trips_so_far))

        self.kpi_labels["avg_q"].config(text=f"{avg_q:.2f}")
        self.kpi_labels["arr_rate"].config(text=f"{arr_rate:.2f}")
        self.kpi_labels["srv_trip"].config(text=f"{srv_trip:.1f}")
        self.kpi_labels["srv_pct"].config(text=f"{srv_pct:.1f}%")

        reconciled = (arrivals_so_far == served_so_far + curr_q)
        self.kpi_labels["reconciled"].config(
            text="✓ Reconciled" if reconciled else "✗ Discrepancy",
            fg="#15803d" if reconciled else "#dc2626"
        )

        dur = self.sim_data["parameters"]["duration"]
        u_display = f"U = {cur['u_value']:.4f}" if cur['u_value'] is not None else "Initial State"
        calc_short = cur.get("calculation", "")
        self.lbl_current_step.config(
            text=f"Minute {self.current_minute}/{dur} ({cur['time_str']})  |  {calc_short}  |  {u_display}  |  Queue: {cur['queue']} pax"
        )

        iid = str(self.current_minute)
        if self.tree.exists(iid):
            self.tree.selection_set(iid)
            self.tree.see(iid)

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel or not self.sim_data:
            return
        minute_idx = int(sel[0])
        steps = self.sim_data["steps"]
        if 0 <= minute_idx < len(steps):
            step = steps[minute_idx]
            u_display = f"U = {step['u_value']:.4f}" if step['u_value'] is not None else "Initial State"
            calc_short = step.get("calculation", "")
            self.lbl_current_step.config(
                text=f"Selected Step {minute_idx} ({step['time_str']})  |  {calc_short}  |  {u_display}  |  Queue: {step['queue']} pax"
            )

    def _show_coprimes_dialog(self):
        if not self.sim_data:
            return

        cfg = self.sim_data["parameters"]
        phi = self.sim_data["euler_phi"]
        m = cfg["modulus"]
        c = cfg["increment"]
        phi_m = phi["phi_m"]
        coprimes = phi.get("coprimes", [])
        gcd_cm = phi["gcd_cm"]
        fact_str = phi.get("factorization_str", f"{m}")
        c_coprime = (gcd_cm == 1)

        dlg = tk.Toplevel(self)
        dlg.title(f"Euler's Phi φ({m}) — Coprime Set Inspection")
        dlg.geometry("540x440")
        dlg.minsize(480, 380)
        dlg.configure(bg="#f8fafc")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg="#0f172a", padx=14, pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(
            hdr, text="Euler's Totient φ(m) — Relatively Prime Set",
            font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#0f172a"
        ).pack(anchor=tk.W)
        tk.Label(
            hdr, text=f"Modulus m = {m}   |   φ({m}) = {phi_m} integers   |   {fact_str}",
            font=("Segoe UI", 9), fg="#94a3b8", bg="#0f172a"
        ).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(dlg, bg="#f8fafc", padx=14, pady=10)
        body.pack(fill=tk.BOTH, expand=True)

        def_box = tk.Frame(body, bg="#f1f5f9", padx=10, pady=8, highlightbackground="#cbd5e1", highlightthickness=1)
        def_box.pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            def_box, text="Mathematical Definition:",
            font=("Segoe UI", 8, "bold"), fg="#1e293b", bg="#f1f5f9"
        ).pack(anchor=tk.W)
        tk.Label(
            def_box,
            text=f"Euler's Phi Function φ(m) counts positive integers k in [1, m] such that gcd(k, m) = 1.\n"
                 f"For m = {m}, exactly {phi_m} out of {m} integers share no common divisor with {m} other than 1.",
            font=("Segoe UI", 8), fg="#475569", bg="#f1f5f9", justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(2, 0))

        list_frame = tk.LabelFrame(
            body, text=f" Coprime Integers up to {m} ({phi_m} values) ",
            font=("Segoe UI", 8, "bold"), bg="#f8fafc", fg="#1e293b", padx=6, pady=6
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        txt = tk.Text(list_frame, wrap=tk.WORD, font=("Consolas", 9), bg="#ffffff", fg="#0f172a",
                      relief=tk.FLAT, bd=0, padx=6, pady=6)
        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        if len(coprimes) <= 250:
            coprimes_display = ", ".join(str(x) for x in coprimes)
        else:
            first_vals = ", ".join(str(x) for x in coprimes[:200])
            coprimes_display = f"{first_vals}\n\n[... and {len(coprimes) - 200} more coprimes (total {len(coprimes)})]"

        txt.insert("1.0", coprimes_display)
        txt.config(state=tk.DISABLED)

        a_val = cfg["multiplier"]
        gcd_am = phi.get("gcd_am", 1)
        a_coprime = (gcd_am == 1)

        lcm_note = tk.Frame(body, bg="#ffffff", padx=10, pady=8,
                            highlightbackground="#0284c7" if (c_coprime and a_coprime) else "#ef4444", highlightthickness=1)
        lcm_note.pack(fill=tk.X, pady=(0, 10))

        c_status_str = f"✓ Increment c = {c} is coprime to m (gcd({c}, {m}) = 1) → Hull-Dobell Cond 1 satisfied" if c_coprime \
            else f"✗ Increment c = {c} is NOT coprime to m (gcd({c}, {m}) = {gcd_cm} ≠ 1) → Suboptimal period"
        a_status_str = f"✓ Multiplier a = {a_val} is in coprime set (gcd({a_val}, {m}) = 1) → Invertible unit" if a_coprime \
            else f"✗ Multiplier a = {a_val} shares factors with m (gcd({a_val}, {m}) = {gcd_am} ≠ 1)"

        tk.Label(
            lcm_note, text="Connection to LCM Parameter Selection:",
            font=("Segoe UI", 8, "bold"), fg="#0f172a", bg="#ffffff"
        ).pack(anchor=tk.W)
        tk.Label(
            lcm_note,
            text=f"• Increment c: {c_status_str}\n"
                 f"• Multiplier a: {a_status_str}\n"
                 f"• Euler's Phi φ({m}) = {phi_m} defines the exact set of valid coprime candidates modulo {m}.",
            font=("Segoe UI", 8), fg="#334155", bg="#ffffff", justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(2, 0))

        btn_bar = tk.Frame(dlg, bg="#f8fafc", padx=14, pady=8)
        btn_bar.pack(fill=tk.X)
        tk.Button(
            btn_bar, text="Close", font=("Segoe UI", 9),
            bg="#ffffff", fg="#0f172a", relief=tk.GROOVE, bd=1,
            padx=14, pady=2, cursor="hand2", command=dlg.destroy
        ).pack(side=tk.RIGHT)

    def _show_phi_calc_dialog(self):
        if not self.sim_data:
            return

        cfg = self.sim_data["parameters"]
        phi = self.sim_data["euler_phi"]
        m = cfg["modulus"]
        phi_m = phi["phi_m"]
        breakdown = phi.get("breakdown", {})
        primes = breakdown.get("primes", [])
        fact_str = breakdown.get("factorization_str", f"{m} = {m}")
        steps = breakdown.get("steps", [])

        dlg = tk.Toplevel(self)
        dlg.title(f"Euler's Phi φ({m}) — Step-by-Step Calculation Breakdown")
        dlg.geometry("540x440")
        dlg.minsize(480, 380)
        dlg.configure(bg="#f8fafc")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg="#0f172a", padx=14, pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(
            hdr, text="Euler's Totient Function φ(m) — Formula Breakdown",
            font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#0f172a"
        ).pack(anchor=tk.W)
        tk.Label(
            hdr, text=f"Modulus m = {m}   |   Result: φ({m}) = {phi_m}",
            font=("Segoe UI", 9), fg="#94a3b8", bg="#0f172a"
        ).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(dlg, bg="#f8fafc", padx=14, pady=10)
        body.pack(fill=tk.BOTH, expand=True)

        card1 = tk.Frame(body, bg="#ffffff", padx=10, pady=8, highlightbackground="#cbd5e1", highlightthickness=1)
        card1.pack(fill=tk.X, pady=(0, 6))
        tk.Label(card1, text="1. Prime Factorization of Modulus m:", font=("Segoe UI", 8, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor=tk.W)
        tk.Label(card1, text=f"   {fact_str}", font=("Consolas", 10, "bold"), fg="#0284c7", bg="#ffffff").pack(anchor=tk.W, pady=(2, 1))
        primes_txt = ", ".join(str(p) for p in primes) if primes else "None (prime / 1)"
        tk.Label(card1, text=f"   Distinct prime factor(s): p ∈ {{{primes_txt}}}", font=("Segoe UI", 8), fg="#475569", bg="#ffffff").pack(anchor=tk.W)

        card2 = tk.Frame(body, bg="#ffffff", padx=10, pady=8, highlightbackground="#cbd5e1", highlightthickness=1)
        card2.pack(fill=tk.X, pady=(0, 6))
        tk.Label(card2, text="2. Euler's Product Formula:", font=("Segoe UI", 8, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor=tk.W)
        tk.Label(card2, text="   φ(n) = n × ∏ (1 − 1/p)    for each distinct prime p dividing n", font=("Consolas", 9, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor=tk.W, pady=(2, 1))
        tk.Label(card2, text="   This formula calculates how many positive integers up to n are coprime to n.", font=("Segoe UI", 8, "italic"), fg="#64748b", bg="#ffffff").pack(anchor=tk.W)

        card3 = tk.Frame(body, bg="#ffffff", padx=10, pady=8, highlightbackground="#cbd5e1", highlightthickness=1)
        card3.pack(fill=tk.X, pady=(0, 6))
        tk.Label(card3, text=f"3. Step-by-Step Calculation for m = {m}:", font=("Segoe UI", 8, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor=tk.W)
        step_text = "\n".join(steps) if steps else f"φ({m}) = {phi_m}"
        tk.Label(card3, text=step_text, font=("Consolas", 9), fg="#0f172a", bg="#ffffff", justify=tk.LEFT).pack(anchor=tk.W, pady=(3, 3))
        tk.Label(card3, text=f"   Final Result: φ({m}) = {phi_m}", font=("Segoe UI", 9, "bold"), fg="#16a34a", bg="#ffffff").pack(anchor=tk.W)

        btn_bar = tk.Frame(dlg, bg="#f8fafc", padx=14, pady=8)
        btn_bar.pack(fill=tk.X)
        tk.Button(
            btn_bar, text="Close", font=("Segoe UI", 9),
            bg="#ffffff", fg="#0f172a", relief=tk.GROOVE, bd=1,
            padx=14, pady=2, cursor="hand2", command=dlg.destroy
        ).pack(side=tk.RIGHT)

