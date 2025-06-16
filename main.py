## GUI
from tkinter import filedialog as fd
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Emoji
from ttkbootstrap.scrolled import ScrolledText
## OpenAI Whisper
import whisper
## Async components
import threading

class MediaPlayer(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=BOTH, expand=YES)
        # Internal state
        self.hdr_var = ttk.StringVar()
        self.elapsed_var = ttk.DoubleVar(value=0)
        self.remain_var = ttk.DoubleVar(value=190)
        # TODO: Use this in display.
        self.playlists = {
            "BERT": [],
            "NaiveBayes": []
        }
        self.current_tab = "BERT"
        # Creating GUI elements
        self.create_header()
        self.create_text_window()
        self.create_progress_meter()
        self.create_buttonbox()

    def create_header(self):
        """The application header to display user messages"""
        self.hdr_var.set("Open a file to begin playback")
        lbl = ttk.Label(
            master=self,
            textvariable=self.hdr_var,
            bootstyle=(LIGHT, INVERSE),
            padding=10
        )
        lbl.pack(fill=X, expand=YES)

    def create_text_window(self):
        """Create frame to contain scrolled text"""
        # Store in self to access later in button
        self.st = ScrolledText(self, padding=5, height=10, autohide=True)
        self.st.pack(fill=BOTH, expand=YES)

    def create_progress_meter(self):
        """Create frame with progress meter with lables"""
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES, pady=10)

        self.elapse = ttk.Label(container, text='00:00')
        self.elapse.pack(side=LEFT, padx=10)

        self.scale = ttk.Scale(
            master=container,
            command=self.on_progress,
            bootstyle=SECONDARY
        )
        self.scale.pack(side=LEFT, fill=X, expand=YES)

        self.remain = ttk.Label(container, text='03:10')
        self.remain.pack(side=LEFT, fill=X, padx=10)

    def create_buttonbox(self):
        """Create buttonbox with media controls"""
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES)
        ttk.Style().configure('TButton', font="-size 14")

        rev_btn = ttk.Button(
            master=container,
            text=Emoji.get('black left-pointing double triangle with vertical bar'),
            padding=10,
        )
        rev_btn.pack(side=LEFT, fill=X, expand=YES)

        play_btn = ttk.Button(
            master=container,
            text=Emoji.get('black right-pointing triangle'),
            padding=10,
        )
        play_btn.pack(side=LEFT, fill=X, expand=YES)

        fwd_btn = ttk.Button(
            master=container,
            text=Emoji.get('black right-pointing double triangle with vertical bar'),
            padding=10,
        )
        fwd_btn.pack(side=LEFT, fill=X, expand=YES)

        pause_btn = ttk.Button(
            master=container,
            text=Emoji.get('double vertical bar'),
            padding=10,
        )
        pause_btn.pack(side=LEFT, fill=X, expand=YES)

        stop_btn = ttk.Button(
            master=container,
            text=Emoji.get('black square for stop'),
            padding=10,
        )
        stop_btn.pack(side=LEFT, fill=X, expand=YES)

        stop_btn = ttk.Button(
            master=container,
            text=Emoji.get('open file folder'),
            bootstyle=SECONDARY,
            command=lambda: self.file_dialog(self.st),
            padding=10
        )
        stop_btn.pack(side=LEFT, fill=X, expand=YES)

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

    def file_dialog(self, text_display):
        file_path = fd.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a")])
        threading.Thread(target=self.transcribe_audio, args=(file_path, text_display, self.current_tab)).start()
        entry = {
            "path": file_path,
            "text": "In Progress"
        }
        self.playlists[self.current_tab].append(entry)

    # TODO: currently operates directly on the text_display. Make it simply transcribe audio into the entry.
    def transcribe_audio(self, file_path, text_display, current_tab):
        text_display.delete("1.0", END)
        text_display.insert(END, "Transcribing... Please wait.\n")
        try:
            result = model.transcribe(file_path)
            text_display.delete("1.0", END)
            text_display.insert(END, result["text"])
            for entry in self.playlists[current_tab]:
                if entry["path"] == file_path:
                    entry["text"] = result["text"]
                    print(entry)
                    return
        except Exception as e:
            text_display.delete("1.0", END)
            text_display.insert(END, f"Error: {e}")

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