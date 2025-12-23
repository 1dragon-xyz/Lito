import os
import asyncio
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import winsound
from datetime import datetime

from logic import TextProcessor, TTSManager

# Try to import version, default to Dev if not found (e.g. running directly without build script)
try:
    from _version import __version__
except ImportError:
    __version__ = "Dev"

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"Lito v{__version__}")
        self.geometry("550x450")
        self.resizable(False, False)

        self.tts_manager = TTSManager()
        self.current_output_path = ""
        self.selected_file_path = ""
        
        # Threading control
        self.cancel_event = threading.Event()
        self.is_converting = False

        self.create_menu()
        self.init_ui()
        
        # Load voices in background
        threading.Thread(target=self.load_voices, daemon=True).start()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About Lito", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def init_ui(self):
        style = ttk.Style()
        style.theme_use('vista')

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header with About Button
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Lito: Text to Speech", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="?", width=3, command=self.show_about).pack(side=tk.RIGHT)

        # Voice Selection
        voice_frame = ttk.Frame(main_frame)
        voice_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(voice_frame, text="Select Voice:").pack(side=tk.LEFT, padx=(0, 10))
        self.voice_var = tk.StringVar(value="Loading voices...")
        self.voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly", width=40)
        self.voice_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Tab 1: Text
        self.tab_text = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_text, text="Text Input")
        self.text_area = tk.Text(self.tab_text, height=10, width=50, wrap=tk.WORD, font=("Segoe UI", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Tab 2: File
        self.tab_file = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_file, text="File Upload")
        self.file_label = ttk.Label(
            self.tab_file, text="No file selected\n(Supported: .txt, .md, .pdf)", 
            relief="groove", anchor="center", padding=30
        )
        self.file_label.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        ttk.Button(self.tab_file, text="Choose File...", command=self.select_file).pack()

        # Progress Bar
        self.progress_frame = ttk.Frame(main_frame)
        self.progress = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X)
        
        # Actions
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(15, 0))
        self.btn_convert = ttk.Button(action_frame, text="Convert to Audio", command=self.toggle_conversion)
        self.btn_convert.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.btn_play = ttk.Button(action_frame, text="Play Audio", command=self.play_audio, state="disabled")
        self.btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.btn_folder = ttk.Button(action_frame, text="Open Folder", command=self.open_folder, state="disabled")
        self.btn_folder.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Status Bar
        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, font=("Segoe UI", 8)).pack(side=tk.BOTTOM, fill=tk.X)

    def show_about(self):
        about_text = (
            f"Lito v{__version__}\n"
            "Simple & Lightweight Text to Speech\n"
            "Copyright © 2024 Lito Project\n\n"
            "Contact & Updates:\n"
            "• Email: anhdhnguyen@gmail.com\n"
            "• X: x.com/1dragon_xyz\n"
            "• GitHub: github.com/1dragon-xyz\n"
            "• LinkedIn: linkedin.com/in/anhdhnguyen"
        )
        messagebox.showinfo("About Lito", about_text)

    def load_voices(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            voices = loop.run_until_complete(self.tts_manager.get_voices())
            loop.close()
            
            formatted_voices = []
            self.voice_mapping = {}
            
            for v in voices:
                display_name = v['FriendlyName']
                formatted_voices.append(display_name)
                self.voice_mapping[display_name] = v['ShortName']

            def update_combo():
                self.voice_combo['values'] = formatted_voices
                if formatted_voices:
                    self.voice_combo.current(0)
                else:
                    self.voice_var.set("No voices found.")
            
            self.after(0, update_combo)
            
        except Exception as e:
            print(f"Error loading voices: {e}")
            self.after(0, lambda: self.voice_var.set("Error loading voices"))

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select Document", filetypes=[("Documents", "*.pdf *.md *.txt"), ("All Files", "*.*")]
        )
        if filename:
            self.selected_file_path = filename
            self.file_label.config(text=os.path.basename(filename))
            self.status_var.set(f"Selected: {filename}")

    def toggle_conversion(self):
        if self.is_converting:
            self.cancel_conversion()
        else:
            self.prepare_conversion()

    def prepare_conversion(self):
        # Gather inputs on Main Thread (fast)
        raw_text = ""
        file_path = None

        if self.notebook.index(self.notebook.select()) == 0:
            raw_text = self.text_area.get("1.0", tk.END).strip()
            if not raw_text:
                messagebox.showwarning("Warning", "Please enter some text.")
                return
        else:
            if not self.selected_file_path:
                messagebox.showwarning("Warning", "Please select a file first.")
                return
            file_path = self.selected_file_path

        # Start UI 'Working' State immediately
        self.is_converting = True
        self.cancel_event.clear()
        
        self.btn_convert.config(text="Cancel Conversion")
        self.btn_play.config(state="disabled")
        self.btn_folder.config(state="disabled")
        
        self.progress_frame.pack(fill=tk.X, pady=(0, 10), before=self.btn_convert.master)
        self.progress.start(10) # Bouncing bar
        self.status_var.set("Processing file...")

        voice_shortname = self.voice_mapping.get(self.voice_combo.get(), "vi-VN-HoaiMyNeural")
        
        # Move ALL logic to background thread to prevent freeze
        threading.Thread(target=self.run_conversion_thread, args=(raw_text, file_path, voice_shortname)).start()

    def cancel_conversion(self):
        if self.is_converting:
            self.status_var.set("Cancelling...")
            self.cancel_event.set()

    def run_conversion_thread(self, raw_text, file_path, voice):
        # Step 1: Heavy Processing (Extract Text)
        text_to_convert = raw_text
        if file_path:
            try:
                text_to_convert = TextProcessor.process_file(file_path)
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda: self.on_error(f"Error reading file: {err_msg}"))
                return

        if not text_to_convert:
            self.after(0, lambda: self.on_error("No text extracted from file."))
            return
            
        # Update UI: Text Ready, Connecting...
        self.after(0, lambda: self.status_var.set("Generating audio..."))

        # Step 2: Conversion
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.tts_manager.output_dir, f"speech_{timestamp}.mp3")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.tts_manager.convert(text_to_convert, voice, output_path, self.cancel_event)
        )
        loop.close()
        
        self.after(0, lambda: self.on_conversion_complete(result, output_path))

    def on_error(self, message):
        self.is_converting = False
        self.progress.stop()
        self.progress_frame.pack_forget()
        self.btn_convert.config(text="Convert to Audio")
        self.status_var.set("Error")
        messagebox.showerror("Error", message)

    def on_conversion_complete(self, result, output_path):
        self.is_converting = False
        self.progress.stop()
        self.progress_frame.pack_forget()
        self.btn_convert.config(text="Convert to Audio")

        if result == "success":
            winsound.MessageBeep(winsound.MB_OK)
            self.current_output_path = output_path
            self.btn_play.config(state="normal")
            self.btn_folder.config(state="normal")
            folder_name = os.path.basename(self.tts_manager.output_dir)
            self.status_var.set(f"Done! Saved to Documents/{folder_name}")
            messagebox.showinfo("Success", "Conversion complete!")
        elif result == "cancelled":
            self.status_var.set("Conversion cancelled.")
        else:
            self.status_var.set("Error during conversion.")
            messagebox.showerror("Error", "Failed to convert text.")

    def play_audio(self):
        if self.current_output_path and os.path.exists(self.current_output_path):
            os.startfile(self.current_output_path)

    def open_folder(self):
        if self.current_output_path and os.path.exists(self.current_output_path):
            subprocess.run(['explorer', '/select,', os.path.normpath(self.current_output_path)])
        else:
            os.startfile(self.tts_manager.output_dir)

if __name__ == "__main__":
    app = App()
    app.mainloop()
