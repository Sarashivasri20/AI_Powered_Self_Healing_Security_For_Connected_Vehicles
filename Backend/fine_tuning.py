import os
import pandas as pd
import torch
import joblib
from sklearn.ensemble import IsolationForest
from transformers import (
    GPT2TokenizerFast,
    GPT2LMHeadModel,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

dataset_files = [
    "data/Attack_free_dataset.txt",
    "data/DoS_attack_dataset.txt",
    "data/Fuzzy_attack_dataset.txt",
    "data/Impersonation_attack_dataset.txt"
]

########################################
# Patch suggestion logic
########################################
def get_patch_for_attack(attack_type, payload):
    if attack_type == "DoS":
        return "Activate the vehicle's security update to handle message overloads."
    elif attack_type == "Fuzzy":
        return "Enable data validity checks to prevent unsafe reads."
    elif attack_type == "Impersonation":
        return "Turn on ID verification to block unauthorized messages."
    elif attack_type == "Attack_free":
        return "No action needed – vehicle is normal."
    else:
        return "No patch suggestion available."

########################################
# Load & Preprocess Data
########################################
def load_and_preprocess_data(dataset_paths):
    data = []

    for file_path in dataset_paths:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue

        attack_type = os.path.basename(file_path).split("_")[0]

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 7:
                continue

            try:
                can_id_hex = parts[3]
                can_id = int(can_id_hex, 16)
                dlc = int(parts[6])

                data_bytes = parts[7 : 7 + dlc]
                byte_values = [int(b, 16) for b in data_bytes]

                while len(byte_values) < 8:
                    byte_values.append(0)

                prompt = (
                    f"Attack type: {attack_type}, "
                    f"CAN ID: {can_id}, DLC: {dlc}, Data: {byte_values} ->"
                )
                response = get_patch_for_attack(attack_type, byte_values)

                data.append({"input_text": prompt, "target_text": response})
            except Exception:
                continue

    return data

# Main

data = load_and_preprocess_data(dataset_files)

if not data:
    print("⚠ No valid lines parsed. Exiting.")
    exit()

# Create Hugging Face dataset
hf_dataset = Dataset.from_dict({
    "input_text": [item["input_text"] for item in data],
    "target_text": [item["target_text"] for item in data]
})

# ✅ Shuffle and select only first 5000 samples
hf_dataset = hf_dataset.shuffle(seed=42).select(range(5000))

# Load tokenizer & model
print("🔧 Loading DistilGPT2...")
tokenizer = GPT2TokenizerFast.from_pretrained("distilgpt2")
tokenizer.pad_token = tokenizer.eos_token
model = GPT2LMHeadModel.from_pretrained("distilgpt2")
model.resize_token_embeddings(len(tokenizer))

# Tokenize
def tokenize_function(examples):
    return tokenizer(
        examples["input_text"],
        padding="max_length",
        truncation=True,
        max_length=128
    )

print("🔧 Tokenizing dataset...")
tokenized_datasets = hf_dataset.map(tokenize_function, batched=True, remove_columns=["input_text", "target_text"])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# ✅ Update base_path to wherever you want to save the model
base_path = "/content"  # or your desired path

# ✅ Faster training config
training_args = TrainingArguments(
    output_dir=os.path.join(base_path, "model/distilgpt2_model"),
    num_train_epochs=1,  # just 1 epoch for now
    per_device_train_batch_size=8,
    logging_dir=os.path.join(base_path, "logs"),
    logging_steps=50,
    save_steps=500,
    save_total_limit=2,
    weight_decay=0.01,
    warmup_steps=100,
    learning_rate=3e-5,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

print("🚀 Starting fine-tuning...")
trainer.train()

# ✅ Save final model
save_path = os.path.join(base_path, "model/fine_tuned_distilgpt2")
trainer.save_model(save_path)
tokenizer.save_pretrained(save_path)

print("✅ Fine-tuning complete!")