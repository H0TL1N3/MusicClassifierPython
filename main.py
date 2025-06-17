## GUI
from tkinter import filedialog as fd
import ttkbootstrap as ttk
from ttkbootstrap.icons import Emoji
from ttkbootstrap.scrolled import ScrolledText
## Audio and utils for it
from pydub import AudioSegment
import simpleaudio as sa
import time
## OpenAI Whisper
import whisper
## Async components
import threading

class MediaPlayer(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
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
        self.elapsed_var = ttk.DoubleVar(value=0)
        self.remain_var = ttk.DoubleVar(value=190)
        self.seeking = False
        # Audio state
        self.current_audio = None
        self.current_play_obj = None
        self.playback_thread = None
        self.is_playing = False
        self.pause_position = 0
        self._stop_playback = threading.Event()
        # Layout
        self.main = None
        self.top = None
        self.left = None
        self.right = None
        self.bottom = None
        # Creating GUI elements
        self.create_layout()
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

    def create_text_window(self):
        """Create frame to contain scrolled text"""
        self.transcribedText = ScrolledText(self.left, padding=5, height=10, autohide=True)
        self.transcribedText.pack(fill="both", expand=True)

    def create_playlists(self):
        """Create frame to contain playlists"""
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
        self.scale.bind("<ButtonPress-1>", self.start_seek)
        self.scale.bind("<ButtonRelease-1>", self.seek_audio)
        self.scale.pack(side="left", fill="x", expand=True)

        self.remain = ttk.Label(container, text='03:10')
        self.remain.pack(side="left", fill="x", padx=10)

    def create_buttonbox(self):
        """Create buttonbox with media controls"""
        container = ttk.Frame(self.bottom)
        container.pack(fill="x", expand=True)
        ttk.Style().configure('TButton', font="-size 14")

        play_btn = ttk.Button(
            master=container,
            text=Emoji.get('black right-pointing triangle'),
            command=self.play_audio,
            padding=10,
        )
        play_btn.pack(side="left", fill="x", expand=True)

        pause_btn = ttk.Button(
            master=container,
            text=Emoji.get('double vertical bar'),
            padding=10,
            command=self.pause_audio
        )
        pause_btn.pack(side="left", fill="x", expand=True)

        stop_btn = ttk.Button(
            master=container,
            text=Emoji.get('black square for stop'),
            command=self.stop_audio,
            padding=10,
        )
        stop_btn.pack(side="left", fill="x", expand=True)

        open_file_btn = ttk.Button(
            master=container,
            text=Emoji.get("open file folder"),
            bootstyle="secondary",
            command=self.file_dialog,
            padding=10
        )
        open_file_btn.pack(side="left", fill="x", expand=True)

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

    ###
    ### Helper functions - audio playback
    ###
    def play_audio(self):
        if self.current_tab is None or self.current_track_index is None:
            return
        # Load info
        track = self.playlists[self.current_tab][self.current_track_index]
        audio_path = track['path']
        # Resume existing playback
        if self.current_audio and self.pause_position > 0:
            self.stop_audio(clear_track=False)
            audio_segment = self.current_audio[self.pause_position:]
        else:
            self.stop_audio(clear_track=False)
            self.current_audio = AudioSegment.from_file(audio_path)
            audio_segment = self.current_audio
        # Load audio
        self.current_play_obj = sa.play_buffer(
            audio_segment.raw_data,
            num_channels=audio_segment.channels,
            bytes_per_sample=audio_segment.sample_width,
            sample_rate=audio_segment.frame_rate,
        )
        # Progress bar init
        self.elapsed_var.set(self.pause_position / 1000 if self.pause_position != 0 else 0)
        self.remain_var.set(self.current_audio.duration_seconds)
        # Start tracking progress
        self._stop_playback.clear()
        self.is_playing = True
        self.playback_thread = threading.Thread(
            target=self.track_progress,
            args=(self.pause_position / 1000,),
            daemon=True
        )
        self.playback_thread.start()

    def track_progress(self, start_offset=0):
        total = self.current_audio.duration_seconds
        start_time = time.time() - start_offset
        while not self._stop_playback.is_set():
            elapsed = time.time() - start_time
            if elapsed >= total:
                break
            # Update GUI values if not currently seeking
            if not self.seeking:
                self.elapsed_var.set(elapsed)
                self.remain_var.set(total - elapsed)
                self.scale.set(elapsed / total)
                self.on_progress(elapsed / total)
            time.sleep(0.2)
        self.is_playing = False

    def pause_audio(self):
        if self.is_playing and self.current_play_obj:
            self._stop_playback.set()
            self.current_play_obj.stop()
            self.pause_position = int(self.elapsed_var.get() * 1000)
            self.is_playing = False

    def stop_audio(self, clear_track=True):
        self._stop_playback.set()
        if self.current_play_obj:
            self.current_play_obj.stop()
        # Reset instance variables
        self.current_play_obj = None
        self.is_playing = False
        if clear_track:
            self.current_audio = None
            self.current_track_index = None
            self.pause_position = 0
            # Reset text and scale
            self.transcribedText.delete("1.0", "end")
            self.elapsed_var.set(0)
            self.remain_var.set(0)
            self.scale.set(0)
            self.elapse.configure(text="00:00")
            self.remain.configure(text="00:00")

    def start_seek(self, event):
        self.seeking = True

    def seek_audio(self, event):
        if not self.current_audio:
            return
        # Kill playback thread safely to avoid scale flicker
        self._stop_playback.set()
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join()
        # Total duration in seconds
        total = self.current_audio.duration_seconds
        # Get the new position from the scale (0.0 to 1.0)
        new_pos_ratio = self.scale.get()
        new_pos_sec = new_pos_ratio * total
        new_pos_ms = int(new_pos_sec * 1000)
        # Set new position
        self.stop_audio(clear_track=False)
        #self.pause_audio()
        self.pause_position = new_pos_ms
        self.play_audio()
        # Stop manual seeking
        self.seeking = False

if __name__ == '__main__':
    root = ttk.Window()
    root.title("Media Player")
    mp = MediaPlayer(root)

    # Load whisper model
    # About available models:
    # https://pypi.org/project/openai-whisper/
    model = whisper.load_model("base.en")

    root.mainloop()