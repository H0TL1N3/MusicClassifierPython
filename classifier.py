import transformers
import trainer
from torch.optim import AdamW
import numpy as np

class Classifier:
    def __init__(self):
        self.trainer = None
        self.tokenizer = None
        self.model_name = None
        self.model = None

    def init(self):
        self.model_name = "bert-base-uncased"
        self.model = transformers.AutoModelForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path="./bert/result",
            num_labels=5)
        training_args = transformers.TrainingArguments(
            output_dir="./results",  # Directory for saving model checkpoints
            eval_strategy="epoch",  # Evaluate at the end of each epoch
            save_strategy="epoch",
            learning_rate=5e-5,  # Start with a small learning rate
            per_device_train_batch_size=1024,  # Batch size per GPU
            per_device_eval_batch_size=1024,
            # auto_find_batch_size=True,
            num_train_epochs=10,  # Number of epochs
            weight_decay=0.01,  # Regularization
            save_total_limit=2,  # Limit checkpoints to save space
            load_best_model_at_end=True,  # Automatically load the best checkpoint
            logging_dir="./logs",  # Directory for logs
            logging_steps=100,  # Log every 100 steps
            fp16=True  # Enable mixed precision for faster training
        )
        self.tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")
        # self.tokenizer.save_pretrained("./bert/tokenizer")
        data_collator = transformers.DataCollatorWithPadding(tokenizer=self.tokenizer)

        self.trainer = transformers.Trainer(
            model=self.model,  # Pre-trained BERT model
            tokenizer=self.tokenizer,
            data_collator=data_collator,  # Efficient batching
        )

        pass

    def classify(self, text: str):
        tokens = self.tokenizer(text, padding="max_length", truncation=True, max_length=128)
        prediction = self.trainer.predict([tokens])
        return np.argmax(prediction.predictions[0])
