import os
import time
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import filedialog, scrolledtext
from datetime import datetime


def set_file_timestamps(file_path):
    now = time.time()
    os.utime(file_path, (now, now))

    EPOCH_DIFF = 116444736000000000
    timestamp = int((now * 10000000) + EPOCH_DIFF)
    ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)

    handle = ctypes.windll.kernel32.CreateFileW(
        file_path, 256, 0, None, 3, 128, None
    )
    if handle != -1:
        ctypes.windll.kernel32.SetFileTime(handle, ctypes.byref(ctime), None, None)
        ctypes.windll.kernel32.CloseHandle(handle)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Date Stamper")
        self.resizable(False, False)

        # --- Folder row ---
        frame_top = tk.Frame(self, padx=10, pady=10)
        frame_top.pack(fill="x")

        self.folder_var = tk.StringVar()
        tk.Entry(frame_top, textvariable=self.folder_var, width=52, state="readonly").pack(side="left")
        tk.Button(frame_top, text="Browse", command=self.browse).pack(side="left", padx=(6, 0))
        tk.Button(frame_top, text="Stamp", command=self.stamp, bg="#2563eb", fg="white",
                  activebackground="#1d4ed8", activeforeground="white").pack(side="left", padx=(6, 0))

        # --- Log area ---
        self.log = scrolledtext.ScrolledText(self, width=70, height=18, state="disabled",
                                             font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
                                             insertbackground="white")
        self.log.pack(padx=10, pady=(0, 10))

        # tags for coloring
        self.log.tag_config("ok", foreground="#4ade80")
        self.log.tag_config("err", foreground="#f87171")
        self.log.tag_config("info", foreground="#93c5fd")

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def log_line(self, text, tag=None):
        self.log.config(state="normal")
        if tag:
            self.log.insert("end", text + "\n", tag)
        else:
            self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def stamp(self):
        folder = self.folder_var.get()
        if not folder:
            self.log_line("No folder selected.", "err")
            return

        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_line(f"Folder : {folder}", "info")
        self.log_line(f"Stamped: {now_str}", "info")
        self.log_line("-" * 60)

        ok = err = 0
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if not os.path.isfile(file_path):
                continue
            try:
                set_file_timestamps(file_path)
                self.log_line(f"  ✓  {filename}", "ok")
                ok += 1
            except Exception as e:
                self.log_line(f"  ✗  {filename}: {e}", "err")
                err += 1

        self.log_line("-" * 60)
        self.log_line(f"Done — {ok} stamped, {err} errors.", "info")


if __name__ == "__main__":
    app = App()
    app.mainloop()
