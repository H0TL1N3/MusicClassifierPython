# Music Classifier GUI program for ValTehPamati course

## Steps to compile
1. Install Python 3.11 on your system as it will be used for this project. 
If you're on Windows, you can get a binary release, version 3.11.9, from [this link](https://www.python.org/downloads/windows/).
2. Set up a virtual environment using either the command line or your IDE of choice. 
Here's a [guide on how to do that in PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#python_create_virtual_env).
3. Install all required libraries from the requirements.txt - once again, 
PyCharm should take care of that and notify you about installing them.
4. You can now compile the project and play around with it.

## Notes about the project
1. Playlists are not saved to storage, which is the intended behavior. 
We keep them in memory during runtime.
2. Accepted notation for keywords and attributes when using `ttkbootstrap` (in this project)
is not through Constants, but through strings -
PyCharm tends to give warnings if Constants are used. 
   1. Please note that `bootstyle` will probably give a warning no matter what approach you use.
   2. Here is some info about [keyword usage in ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/gettingstarted/tutorial/#keyword-usage).

## IMPORTANT: Please Note that the project is not yet complete.
### TODO List:
1. Add models (BERT, NB)...
2. Implement functions that will classify the text.
### DONE List:
1. Basic layout for the app.
2. Playlist functionality.
3. File addition.
4. Audio transcription using OpenAI Whisper.
5. Playback and seeking of audio.
6. Color guides to show the result of the classification