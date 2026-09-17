import tkinter as tk
from ui.simulator_window import SimulatorWindow

def main():
    root = tk.Tk()
    root.withdraw()
    app = SimulatorWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
