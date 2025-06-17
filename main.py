## GUI
from tkinter import filedialog as fd
import ttkbootstrap as ttk
from ttkbootstrap.icons import Emoji
from ttkbootstrap.scrolled import ScrolledText
## OpenAI Whisper
import whisper
## Async components
import threading

class MediaPlayer(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        # Internal state
        self.hdr_var = ttk.StringVar()
        self.elapsed_var = ttk.DoubleVar(value=0)
        self.remain_var = ttk.DoubleVar(value=190)
        # Playlist and chosen track state
        self.playlists = {
            "BERT": [],
            "NaiveBayes": []
        }
        self.current_tab = "BERT"
        self.notebook = None
        self.playlist_frames = {}
        self.current_track_index = None
        # Scrolled Text state
        self.transcribedText = None
        # Progress bar state
        self.elapse = None
        self.scale = None
        self.remain = None
        # Layout
        self.main = None
        self.top = None
        self.left = None
        self.right = None
        self.bottom = None
        # Creating GUI elements
        self.create_layout()
        self.create_header()
        self.create_text_window()
        self.create_playlists()
        self.create_progress_meter()
        self.create_buttonbox()

    def create_layout(self):
        self.main = ttk.Frame(self)
        self.main.pack(fill="both", expand=True)
        self.top = ttk.Frame(self.main)
        self.top.pack(side="top", fill="both", expand=True)
        self.left = ttk.Frame(self.top)
        self.left.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.right = ttk.Frame(self.top)
        self.right.pack(side="right", fill="y", padx=5, pady=5)
        self.bottom = ttk.Frame(self.main)
        self.bottom.pack(side="bottom", fill="both", padx=5, pady=5)

    def create_header(self):
        """The application header to display user messages"""
        self.hdr_var.set("Open a file to begin playback")
        lbl = ttk.Label(
            master=self,
            textvariable=self.hdr_var,
            bootstyle="light-inverse",
            padding=10
        )
        lbl.pack(fill="x", expand=True)

    def create_text_window(self):
        """Create frame to contain scrolled text"""
        # Store in self to access later
        self.transcribedText = ScrolledText(self.left, padding=5, height=10, autohide=True)
        self.transcribedText.pack(fill="both", expand=True)

    def create_playlists(self):
        """Create frame to contain playlists"""
        # Store in self to access later
        self.notebook = ttk.Notebook(self.right)
        self.notebook.pack(fill="both", expand=True)
        self.playlist_frames = {}

        for tab_name in self.playlists.keys():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=tab_name)
            # Inner frame for entries in playlist
            content_frame = ttk.Frame(frame)
            content_frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.playlist_frames[tab_name] = content_frame
            self.render_playlist(tab_name)

        # Handle tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def create_progress_meter(self):
        """Create frame with progress meter with labels"""
        container = ttk.Frame(self.bottom)
        container.pack(fill="x", expand=True, pady=10)

        self.elapse = ttk.Label(container, text='00:00')
        self.elapse.pack(side="left", padx=10)

        self.scale = ttk.Scale(
            master=container,
            command=self.on_progress,
            bootstyle="secondary"
        )
        self.scale.pack(side="left", fill="x", expand=True)

        self.remain = ttk.Label(container, text='03:10')
        self.remain.pack(side="left", fill="x", padx=10)

    def create_buttonbox(self):
        """Create buttonbox with media controls"""
        container = ttk.Frame(self.bottom)
        container.pack(fill="x", expand=True)
        ttk.Style().configure('TButton', font="-size 14")

        rev_btn = ttk.Button(
            master=container,
            text=Emoji.get('black left-pointing double triangle with vertical bar'),
            padding=10,
        )
        rev_btn.pack(side="left", fill="x", expand=True)

        play_btn = ttk.Button(
            master=container,
            text=Emoji.get('black right-pointing triangle'),
            padding=10,
        )
        play_btn.pack(side="left", fill="x", expand=True)

        fwd_btn = ttk.Button(
            master=container,
            text=Emoji.get('black right-pointing double triangle with vertical bar'),
            padding=10,
        )
        fwd_btn.pack(side="left", fill="x", expand=True)

        pause_btn = ttk.Button(
            master=container,
            text=Emoji.get('double vertical bar'),
            padding=10,
        )
        pause_btn.pack(side="left", fill="x", expand=True)

        stop_btn = ttk.Button(
            master=container,
            text=Emoji.get('black square for stop'),
            padding=10,
        )
        stop_btn.pack(side="left", fill="x", expand=True)

        stop_btn = ttk.Button(
            master=container,
            text=Emoji.get("open file folder"),
            bootstyle="secondary",
            command=lambda: self.file_dialog(),
            padding=10
        )
        stop_btn.pack(side="left", fill="x", expand=True)

    def on_progress(self, val: float):
        """Update progress labels when the scale is updated."""
        elapsed = self.elapsed_var.get()
        remaining = self.remain_var.get()
        total = int(elapsed + remaining)

        elapse = int(float(val) * total)
        elapse_min = elapse // 60
        elapse_sec = elapse % 60

        remain_tot = total - elapse
        remain_min = remain_tot // 60
        remain_sec = remain_tot % 60

        self.elapsed_var.set(elapse)
        self.remain_var.set(remain_tot)

        self.elapse.configure(text=f'{elapse_min:02d}:{elapse_sec:02d}')
        self.remain.configure(text=f'{remain_min:02d}:{remain_sec:02d}')

    ###
    ### Helper functions
    ###
    def on_tab_change(self, event):
        selected_index = self.notebook.index("current")
        self.current_tab = list(self.playlists.keys())[selected_index]
        self.current_track_index = None
        self.transcribedText.delete("1.0", "end")

    def render_playlist(self, playlist_name):
        # Get
        frame = self.playlist_frames.get(playlist_name)
        if not frame:
            return
        # Clear
        for widget in frame.winfo_children():
            widget.destroy()
        # Fill
        for index, entry in enumerate(self.playlists[playlist_name]):
            filename = entry["path"].split("/")[-1]
            btn = ttk.Button(
                frame,
                text=filename,
                bootstyle="secondary",
                command=lambda idx=index, name=playlist_name: self.select_track(name, idx)
            )
            btn.pack(fill="x", pady=2)

    def select_track(self, playlist_name, index):
        entry = self.playlists[playlist_name][index]
        # Redundant change of playlist, but may be useful in some scenarios
        self.current_tab = playlist_name
        self.current_track_index = index

        self.transcribedText.delete("1.0", "end")
        self.transcribedText.insert("end", entry["text"])

    def file_dialog(self):
        file_path = fd.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a")])
        self.add_track(file_path, self.current_tab)
        threading.Thread(target=self.transcribe_audio, args=(file_path, self.current_tab)).start()

    def add_track(self, file_path, tab):
        entry = {
            "path": file_path,
            "text": "In Progress"
        }
        self.playlists[tab].append(entry)
        self.render_playlist(tab)

    def transcribe_audio(self, file_path, tab):
        try:
            result = model.transcribe(file_path)
            print("done")
            for idx, entry in enumerate(self.playlists[tab]):
                if entry["path"] == file_path:
                    self.playlists[tab][idx]["text"] = result["text"]
                    # TODO: Test later that this callback works correctly.
                    # Callback to rerender lyrics
                    if idx == self.current_track_index:
                        self.select_track(tab, idx)
        except Exception as e:
            for entry in self.playlists[self.current_tab]:
                if entry["path"] == file_path:
                    entry["text"] = f"Error during transcription: {e}"

if __name__ == '__main__':
    root = ttk.Window()
    root.title("Media Player")
    mp = MediaPlayer(root)

    # Load whisper model
    # About available models:
    # https://pypi.org/project/openai-whisper/
    model = whisper.load_model("base.en")

    mp.scale.set(0.35)
    root.mainloop()