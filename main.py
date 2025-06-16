## GUI
from tkinter import filedialog as fd
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# TODO: might not be needed.
from ttkbootstrap.scrolled import ScrolledText
## OpenAI Whisper
import whisper
## Async components
import threading

# TODO: Repurpose and remove this later.
def transcribe_audio(file_path, text_display):
    text_display.delete("1.0", END)
    text_display.insert(END, "Transcribing... Please wait.\n")
    try:
        result = model.transcribe(file_path)
        text_display.delete("1.0", END)
        text_display.insert(END, result["text"])
    except Exception as e:
        text_display.delete("1.0", END)
        text_display.insert(END, f"Error: {e}")

# TODO: Repurpose and remove this later.
def select_file(text_display):
    file_path = fd.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a")])
    if file_path:
        # Run transcription in a separate thread to avoid freezing the GUI
        threading.Thread(target=transcribe_audio, args=(file_path, text_display)).start()

# Launch the app
root = ttk.Window()
root.title("Whisper Audio Transcriber")
root.geometry("600x400")

# Load whisper model
# About available models:
# https://pypi.org/project/openai-whisper/
model = whisper.load_model("base.en")

# Title label
ttk.Label(root, text="Audio to Text Transcriber", font=("Helvetica", 18)).pack(pady=10)

# Transcription display
st = ScrolledText(root, padding=5, height=10, autohide=True)
st.pack(fill=BOTH, expand=YES)

# Button to select audio file
ttk.Button(root, text="Choose Audio File", bootstyle="primary", command=lambda: select_file(st)).pack(pady=10)

# Launch app
root.mainloop()