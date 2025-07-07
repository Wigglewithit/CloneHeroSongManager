import os
import time
import threading
import zipfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SongZipHandler(FileSystemEventHandler):
    def __init__(self, log_func, status_func, songs_folder):
        self.log = log_func
        self.update_status = status_func
        self.songs_folder = songs_folder

    def on_created(self, event):
        if event.src_path.endswith('.zip'):
            time.sleep(2)  # wait to ensure download completed
            self.update_status("New zip found")
            self.log(f"📦 Found zip: {event.src_path}")
            self.extract_and_move(event.src_path)

    def extract_and_move(self, zip_path):
        try:
            self.update_status("Extracting zip...")
            temp_folder = os.path.splitext(zip_path)[0]
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_folder)
                self.log(f"✅ Extracted to: {temp_folder}")

            self.update_status("Moving files to Songs folder...")
            for item in os.listdir(temp_folder):
                item_path = os.path.join(temp_folder, item)
                if os.path.isdir(item_path):
                    dest = os.path.join(self.songs_folder, item)
                    shutil.move(item_path, dest)
                    self.log(f"🎵 Moved '{item}' to Clone Hero Songs")
                else:
                    self.log(f"⚠️ Skipped non-folder file: {item_path}")

            shutil.rmtree(temp_folder)
            os.remove(zip_path)
            self.log("🧹 Cleaned up temporary files and zip.")
            self.update_status("Done!")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.update_status("Error")

class CloneHeroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clone Hero Song Manager")
        self.observer = None
        self.handler = None

        self.download_path = tk.StringVar()
        self.songs_path = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Zip Folder to Watch").grid(row=0, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.download_path, width=50).grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.select_download_folder).grid(row=0, column=2)

        tk.Label(self.root, text="Clone Hero Songs Folder").grid(row=1, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.songs_path, width=50).grid(row=1, column=1)
        tk.Button(self.root, text="Browse", command=self.select_songs_folder).grid(row=1, column=2)

        self.start_button = tk.Button(self.root, text="Start Watching", command=self.toggle_watching)
        self.start_button.grid(row=2, column=1, pady=10)

        self.status_label = tk.Label(self.root, text="Status: Idle", fg="blue")
        self.status_label.grid(row=2, column=0, sticky="w", padx=10)

        self.log_box = scrolledtext.ScrolledText(self.root, width=70, height=15, state='disabled')
        self.log_box.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, f"{message}\n")
        self.log_box.config(state='disabled')
        self.log_box.yview(tk.END)

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")
        self.root.update_idletasks()

    def select_download_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.download_path.set(path)

    def select_songs_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.songs_path.set(path)

    def toggle_watching(self):
        if self.observer is None:
            if not self.download_path.get() or not self.songs_path.get():
                messagebox.showwarning("Missing Paths", "Please select both folders.")
                return

            self.handler = SongZipHandler(self.log, self.update_status, self.songs_path.get())
            self.observer = Observer()
            self.observer.schedule(self.handler, self.download_path.get(), recursive=False)
            self.observer.start()
            self.start_button.config(text="Stop Watching")
            self.update_status("Watching for song zips...")
            self.log("🟢 Started watching for song zips...")
        else:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.start_button.config(text="Start Watching")
            self.update_status("Idle")
            self.log("🛑 Stopped watching.")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = CloneHeroApp(root)
    root.mainloop()
