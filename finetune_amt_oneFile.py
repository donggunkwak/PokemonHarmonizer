import os
import sys
import random
# import bitsandbytes as bnb
from datasets import load_dataset
from torch.optim import AdamW
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, GPT2LMHeadModel
from torch.utils.data import SequentialSampler, Subset
from datasets import Dataset, DatasetDict
from tqdm import tqdm
from transformers import DataCollatorForLanguageModeling
from torch.nn.utils.rnn import pad_sequence
import torch
import sys

def parse_amt_tokens(token_file):
    lines = open(token_file).readlines()

    all_tokens = []

    for l in lines:
        token_text = l.strip()
        tokens = [int(t) for t in token_text.split(" ")]
        # print(len(tokens), tokens[:10])

        all_tokens.append(tokens)

    return all_tokens

def load_tokenized_data(filename, train_ratio=0.8, seed=42, max_length=1024, vocab_size=55028):
    data = []
    all_tokens = parse_amt_tokens(filename)
    for tokens in all_tokens:
        if len(tokens) > 1 and not any([t >= vocab_size for t in tokens]):
            # Truncate if too long
            tokens = tokens[:max_length]
            
            # Pad with SEQ token
            if len(tokens) < max_length:
                tokens += [50256] * (max_length - len(tokens))

            data.append({"input_ids": tokens, "labels": tokens.copy()})
    else:
        print(len(tokens))
    if not data:
        raise ValueError("No valid tokenized data found!")

    random.seed(seed)
    random.shuffle(data)
    split_idx = int(len(data) * train_ratio)

    ds_train = Dataset.from_list(data[:split_idx])
    ds_valid = Dataset.from_list(data[split_idx:])

    return DatasetDict({"train": ds_train, "valid": ds_valid})

def debug_collate_fn(features, max_token_id=55028):
    """
    A collate function that checks if any token in input_ids or labels
    exceeds max_token_id, and if so, skips that entire sample.
    """
    valid_features = []
    for i, feature in enumerate(features):
        input_ids = feature["input_ids"]
        labels = feature["labels"]
        
        # Check input_ids
        if any(t > max_token_id for t in input_ids):
            print(f"[WARNING] Found out-of-range token in sample {i} (input_ids): {input_ids}")
            continue
        
        # Check labels
        if any(t > max_token_id for t in labels):
            print(f"[WARNING] Found out-of-range token in sample {i} (labels): {labels}")
            continue
        
        valid_features.append(feature)
    
    # If every feature in the batch is invalid, raise an error (or you could return an empty batch).
    if not valid_features:
        raise ValueError("All samples in this batch contained out-of-range tokens!")
    else:
        print("Valid samples:", len(valid_features))
    
    # Convert to tensors.
    batch_input_ids = [torch.tensor(f["input_ids"], dtype=torch.long) for f in valid_features]
    batch_labels    = [torch.tensor(f["labels"],    dtype=torch.long) for f in valid_features]
    
    # Stack into a single batch tensor.
    input_ids = torch.stack(batch_input_ids, dim=0)
    labels    = torch.stack(batch_labels, dim=0)

    return {"input_ids": input_ids, "labels": labels}


GPT2_MODEL_NAME = "stanford-crfm/music-medium-800k"
CKPT_DIR = "amt_PKMN_BW_finetune_med"
SEQLEN = 1024
LR = 1e-5

class SequentialTrainer(Trainer):
    """(Shih-Lun) for fair comparison at same training steps, no shuffling"""
    def _get_train_sampler(self):
        return SequentialSampler(self.train_dataset)

if __name__ == "__main__":

    model = AutoModelForCausalLM.from_pretrained(
        GPT2_MODEL_NAME).to("cuda")
    
    embedding_size = model.get_input_embeddings().num_embeddings
    print("Model embedding size:", embedding_size)

    print("total trainable params:", sum(p.numel() for p in model.parameters() if p.requires_grad))

    # ENTER PATH TO TOKENIZED MIDI FILES HERE
    dataset_dict = load_tokenized_data("C:/Users/dongg/Documents/UROPSP25/PokemonTraining_BW/pokemon_midi_dataset/tokenized-events-black_white_filtered.txt")
    ds_train = dataset_dict["train"]
    ds_valid = dataset_dict["valid"]

    for i, sample in enumerate(ds_train):
      for t in sample["input_ids"]:
            if t >= embedding_size:
                print(f"Out-of-range token found in sample {i}, token={t}")

    print(ds_train[0])
    optimizer = AdamW(model.parameters(), lr=LR)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=CKPT_DIR,
        learning_rate=LR,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        lr_scheduler_type="cosine",
        max_steps=1000,
        save_steps=2000,
        logging_dir="./logs",
        eval_steps=2000,
        logging_steps=10,
        bf16=True,  # Enable mixed precision
        report_to="wandb",
        dataloader_num_workers=4,
        do_eval=True,
        gradient_accumulation_steps=4,
        save_safetensors=False,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds_train,
        eval_dataset=ds_valid,
        optimizers=(optimizer, None),
        data_collator=debug_collate_fn,  # Add this
    )


    # Train
    trainer.train()