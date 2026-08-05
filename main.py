import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from gui.login import LoginWindow

os.makedirs(os.path.join(os.path.dirname(__file__), "photos"), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), "backup"), exist_ok=True)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
