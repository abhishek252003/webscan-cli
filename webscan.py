import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import requests
import threading
import queue

class CategorizedScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Web Scanner")
        self.root.geometry("1000x600")

        self.stop_event = threading.Event()
        self.word_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.total_words = 0

        self.tab_titles = {
            '2xx': "Success (2xx)",
            '403': "Forbidden (403)",
            '3xx': "Redirects (3xx)",
            '5xx': "Server Errors (5xx)"
        }

        self.create_widgets()
        self.update_results()

    def create_widgets(self):
        # --- Top input frame ---
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill="x")
        
        input_grid = tk.Frame(top_frame)
        input_grid.pack(fill="x")
        input_grid.columnconfigure(1, weight=1)

        tk.Label(input_grid, text="Target URL:").grid(row=0, column=0, sticky="w", pady=2)
        self.url_entry = tk.Entry(input_grid)
        self.url_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(input_grid, text="Wordlist File:").grid(row=1, column=0, sticky="w", pady=2)
        self.wordlist_entry = tk.Entry(input_grid)
        self.wordlist_entry.grid(row=1, column=1, sticky="ew")
        tk.Button(input_grid, text="Browse...", command=self.select_wordlist).grid(row=1, column=2, padx=(5,0))

        tk.Label(input_grid, text="Threads:").grid(row=2, column=0, sticky="w", pady=2)
        self.thread_spinbox = tk.Spinbox(input_grid, from_=1, to=100, width=5)
        self.thread_spinbox.delete(0, "end")
        self.thread_spinbox.insert(0, "10")
        self.thread_spinbox.grid(row=2, column=1, sticky="w")

        # --- Control buttons ---
        control_frame = tk.Frame(self.root, pady=5)
        control_frame.pack()
        self.start_button = tk.Button(control_frame, text="Start Scan", command=self.start_scan, font=("Helvetica", 10, "bold"))
        self.start_button.pack(side="left", padx=5)
        self.stop_button = tk.Button(control_frame, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=5)

        # --- Nested PanedWindow for side-by-side results ---
        pane1 = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        pane1.pack(pady=10, padx=10, fill="both", expand=True)
        pane2 = tk.PanedWindow(pane1, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        pane3 = tk.PanedWindow(pane2, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)

        self.tabs = {}
        frame_2xx = ttk.Labelframe(pane1, text=self.tab_titles['2xx'], padding=5)
        self.tabs['2xx'] = scrolledtext.ScrolledText(frame_2xx, wrap=tk.WORD, height=15)
        self.tabs['2xx'].pack(fill="both", expand=True)
        pane1.add(frame_2xx)
        pane1.add(pane2)

        frame_403 = ttk.Labelframe(pane2, text=self.tab_titles['403'], padding=5)
        self.tabs['403'] = scrolledtext.ScrolledText(frame_403, wrap=tk.WORD, height=15)
        self.tabs['403'].pack(fill="both", expand=True)
        pane2.add(frame_403)
        pane2.add(pane3)

        frame_3xx = ttk.Labelframe(pane3, text=self.tab_titles['3xx'], padding=5)
        self.tabs['3xx'] = scrolledtext.ScrolledText(frame_3xx, wrap=tk.WORD, height=15)
        self.tabs['3xx'].pack(fill="both", expand=True)
        pane3.add(frame_3xx)

        frame_5xx = ttk.Labelframe(pane3, text=self.tab_titles['5xx'], padding=5)
        self.tabs['5xx'] = scrolledtext.ScrolledText(frame_5xx, wrap=tk.WORD, height=15)
        self.tabs['5xx'].pack(fill="both", expand=True)
        pane3.add(frame_5xx)
        
        self.tabs['2xx'].tag_config("found", foreground="green")
        self.tabs['403'].tag_config("forbidden", foreground="red")
        self.tabs['3xx'].tag_config("redirect", foreground="blue")
        self.tabs['5xx'].tag_config("error", foreground="orange")
        
        tk.Button(self.root, text="Save Results", command=self.save_results).pack(pady=(0, 5))
        
        # --- Status Bar with Hint ---
        status_frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar = tk.Label(status_frame, text="Ready", anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, padx=5)
        hint_label = tk.Label(status_frame, text="Drag dividers <|> to resize panes", anchor=tk.E, fg="grey")
        hint_label.pack(side=tk.RIGHT, padx=5)
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def select_wordlist(self):
        filepath = filedialog.askopenfilename(title="Select a Wordlist File", filetypes=(("Text files", "*.txt"),))
        if filepath:
            self.wordlist_entry.delete(0, tk.END)
            self.wordlist_entry.insert(0, filepath)

    def start_scan(self):
        target_url = self.url_entry.get().strip()
        wordlist_path = self.wordlist_entry.get().strip()
        num_threads = int(self.thread_spinbox.get())
        if not target_url.startswith('http'):
             messagebox.showerror("Error", "URL must start with http:// or https://")
             return
        if not wordlist_path:
            messagebox.showerror("Error", "Please provide a wordlist file.")
            return
        for tab in self.tabs.values():
            tab.delete('1.0', tk.END)
        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_bar.config(text="Scanning...")
        try:
            with open(wordlist_path, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
                self.total_words = len(words)
                for word in words:
                    self.word_queue.put(word)
        except FileNotFoundError:
            messagebox.showerror("Error", "Wordlist file not found.")
            self.reset_ui()
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not read wordlist: {e}")
            self.reset_ui()
            return
        self.progress_bar["maximum"] = self.total_words
        self.progress_bar["value"] = 0
        for _ in range(num_threads):
            threading.Thread(target=self.worker, args=(target_url,), daemon=True).start()

    def stop_scan(self):
        self.status_bar.config(text="Stopping...")
        self.stop_event.set()
        self.stop_button.config(state=tk.DISABLED)

    def worker(self, base_url):
        base_url = base_url.rstrip('/')
        while not self.word_queue.empty() and not self.stop_event.is_set():
            try:
                word = self.word_queue.get_nowait()
                full_url = f"{base_url}/{word}"
                try:
                    response = requests.get(full_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=False)
                    if response.status_code != 404:
                        result = (response.status_code, f"{full_url} (Status: {response.status_code})")
                        self.results_queue.put(result)
                except requests.RequestException:
                    pass
            except queue.Empty:
                break
        self.word_queue.task_done()

    def update_results(self):
        try:
            while not self.results_queue.empty():
                status_code, result_str = self.results_queue.get_nowait()
                if 200 <= status_code < 300:
                    self.tabs['2xx'].insert(tk.END, result_str + "\n", "found")
                elif status_code == 403:
                    self.tabs['403'].insert(tk.END, result_str + "\n", "forbidden")
                elif 300 <= status_code < 400:
                    self.tabs['3xx'].insert(tk.END, result_str + "\n", "redirect")
                elif 500 <= status_code < 600:
                    self.tabs['5xx'].insert(tk.END, result_str + "\n", "error")
            if self.start_button['state'] == tk.DISABLED:
                processed_count = self.total_words - self.word_queue.qsize()
                self.progress_bar["value"] = processed_count
                if processed_count == self.total_words and self.word_queue.empty():
                    if not self.stop_event.is_set(): self.status_bar.config(text="Scan Finished!")
                    else: self.status_bar.config(text="Scan Stopped.")
                    self.reset_ui()
        finally:
            self.root.after(100, self.update_results)

    def reset_ui(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def save_results(self):
        all_content = ""
        for text_widget in self.tabs.values():
            all_content += text_widget.get("1.0", tk.END).strip()
        if not all_content:
            messagebox.showwarning("No Results", "There are no results to save.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Scan Results"
        )
        if not filepath:
            return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for code_range, tab_title in self.tab_titles.items():
                    text_widget = self.tabs[code_range]
                    content = text_widget.get("1.0", tk.END).strip()
                    if content:
                        f.write(f"--- Results for {tab_title} ---\n")
                        f.write(content + "\n\n")
            messagebox.showinfo("Success", f"Results successfully saved to {filepath}")
        except (IOError, PermissionError) as e:
            messagebox.showerror("Save Error", f"Failed to save file.\n\nError: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CategorizedScannerApp(root)
    root.mainloop()