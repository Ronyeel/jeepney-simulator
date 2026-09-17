import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ui.theme import (
    BG_PANEL,
    BORDER,
    TEXT_MAIN,
    TEXT_MUTED,
    ACCENT_BLUE,
    FONT_BOLD,
    FONT_SM,
)

class TelemetryTable(tk.Frame):
    def __init__(self, parent, on_select_step):
        super().__init__(parent, bg=BG_PANEL, padx=4, pady=4)
        self.on_select_step = on_select_step
        self.sim_data = None

        ctrls = tk.Frame(self, bg=BG_PANEL)
        ctrls.pack(fill=tk.X, pady=(0, 4))

        tk.Label(ctrls, text="Minute-by-minute transit queue dispatch log:", font=FONT_SM, fg=TEXT_MUTED, bg=BG_PANEL).pack(side=tk.LEFT)

        cols = ("time", "lcm", "arrivals", "jeepney", "served", "queue")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)

        self.tree.heading("time", text="Timestamp")
        self.tree.heading("lcm", text="LCM Value X(n)")
        self.tree.heading("arrivals", text="Passenger Inflow")
        self.tree.heading("jeepney", text="Jeepney Event")
        self.tree.heading("served", text="Boarded (Served)")
        self.tree.heading("queue", text="Queue Balance")

        self.tree.column("time", width=85, anchor=tk.CENTER)
        self.tree.column("lcm", width=110, anchor=tk.CENTER)
        self.tree.column("arrivals", width=105, anchor=tk.CENTER)
        self.tree.column("jeepney", width=130, anchor=tk.CENTER)
        self.tree.column("served", width=105, anchor=tk.CENTER)
        self.tree.column("queue", width=105, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def populate(self, sim_data):
        self.sim_data = sim_data
        for item in self.tree.get_children():
            self.tree.delete(item)

        for step in sim_data["steps"]:
            j_txt = "YES (Dispatched)" if step["jeepney_arrived"] else "--"
            self.tree.insert(
                "",
                tk.END,
                text=str(step["minute"]),
                values=(
                    step["time_str"],
                    step["lcm_value"],
                    f"+{step['arrivals']} pax" if step["minute"] > 0 else "Seed",
                    j_txt,
                    f"{step['served']} boarded" if step["jeepney_arrived"] else "--",
                    f"{step['queue']} waiting"
                )
            )

    def select_minute(self, minute_idx):
        self._updating_selection = True
        try:
            for item in self.tree.get_children():
                if self.tree.item(item, "text") == str(minute_idx):
                    if item not in self.tree.selection():
                        self.tree.selection_set(item)
                    self.tree.see(item)
                    break
        finally:
            self._updating_selection = False

    def _on_select(self, event):
        if getattr(self, "_updating_selection", False):
            return
        sel = self.tree.selection()
        if not sel:
            return
        minute_idx = int(self.tree.item(sel[0], "text"))
        self.on_select_step(minute_idx)
