import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Create root application
root = tk.Tk()

# Add fancy buttons
b1 = ttk.Button(root, text="Button 1", bootstyle=SUCCESS)
b1.pack(side=LEFT, padx=5, pady=10)
b2 = ttk.Button(root, text="Button 2", bootstyle=(INFO, OUTLINE))
b2.pack(side=LEFT, padx=5, pady=10)

# Launch app
root.mainloop()