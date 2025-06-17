# Music Classifier GUI program for ValTehPamati course

## Steps to compile
1. Install Python 3.11 on your system as it will be used for this project. 
If you're on Windows, you can get a binary release, version 3.11.9, from [this link](https://www.python.org/downloads/windows/).
2. Set up a virtual environment using either the command line or your IDE of choice. 
Here's a [guide on how to do that in PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#python_create_virtual_env).
3. Before installing everything from `requirements.txt`, run these two commands in your virtual environment - 
In PyCharm, you can use the `Terminal` window, available in the bottom-left corner:
   1. `pip install "cython<3.0.0" wheel`
   2. `pip install "pyyaml==5.4.1" --no-build-isolation`
4. Install all required libraries from the requirements.txt - once again, 
PyCharm should take care of that and notify you about installing them.
5. Download the BERT model from [this Google Drive link](https://drive.google.com/file/d/1PVphOyRvdsZ8oPqB8vWT5yOw6yBkJlGC/view?usp=drive_link).
Then, unzip the contents of the downloaded `.zip` file in the `bert` directory at the root of the project.
   1. Make sure the resulting `bert` folder is not nested inside another `bert` folder.
   2. The BERT model was not pushed to the repo, as its size exceeds 2GiB, which is more than what GitHub allows.
6. You can now compile the project and play around with it.

## Notes about the project
1. Playlists are not saved to storage, which is the intended behavior. 
We keep them in memory during runtime.
2. Accepted notation for keywords and attributes when using `ttkbootstrap` (in this project)
is not through Constants, but through strings -
PyCharm tends to give warnings if Constants are used. 
   1. Please note that `bootstyle` will probably give a warning no matter what approach you use.
   2. Here is some info about [keyword usage in ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/gettingstarted/tutorial/#keyword-usage).

## IMPORTANT: Please Note that the project is not yet complete.
### DONE List:
1. Basic layout for the app.
2. Playlist functionality.
3. File addition.
4. Audio transcription using OpenAI Whisper.
5. Playback and seeking of audio.
6. Color guides to show the result of the classification
7. Functions that classify the text.
8. BERT classifier
9. GaussianNaiveBayes classifier
10. Added Jupyter Notebooks
