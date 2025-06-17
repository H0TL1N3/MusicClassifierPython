import os
import pickle
import transformers
import trainer
from torch.optim import AdamW
import numpy as np


class NBClassifier:
    def __init__(self):
        self.nb = None
        self.vectorizer = None
        self.id_to_class = {"rb": "R&B", "rock": "Rock", "country": "Country", "pop": "Pop", "rap": "Rap"}

    def init(self):
        if os.path.isfile('./NB/vectorizer.pk'):
            with open('./NB/vectorizer.pk', 'rb') as fin:
                self.vectorizer = pickle.load(fin)
        if os.path.isfile('./NB/gnb.pk'):
            with open('./NB/gnb.pk', 'rb') as fin:
                self.nb = pickle.load(fin)
        pass

    def classify(self, text: str):
        tokens = self.vectorizer.transform([text])
        prediction = self.nb.predict(tokens[0].toarray())
        return str(prediction[0])
