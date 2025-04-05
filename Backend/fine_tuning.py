import os
import torch
from transformers import (
    GPT2TokenizerFast,
    GPT2LMHeadModel,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

# Dataset file paths
dataset_files = [
    "data/Attack_free_dataset.txt",
    "data/DoS_attack_dataset.txt",
    "data/Fuzzy_attack_dataset.txt",
    "data/Impersonation_attack_dataset.txt"
]

########################################
# Patch + Explanation logic
########################################
def get_patch_and_explanation_for_attack(attack_type, payload):
    if attack_type == "DoS":
        explanation = "A DoS attack floods the CAN bus with high-priority messages, preventing normal communication."
        patch = "Activate the vehicle's security update to handle message overloads."
    elif attack_type == "Fuzzy":
        explanation = "A Fuzzy attack sends malformed or random data to confuse or crash ECUs."
        patch = "Enable data validity checks to prevent unsafe reads."
    elif attack_type == "Impersonation":
        explanation = "An Impersonation attack uses spoofed IDs to mimic legitimate ECUs and inject malicious data."
        patch = "Turn on ID verification to block unauthorized messages."
    elif attack_type == "Attack_free":
        explanation = "No attack detected. All vehicle systems appear to be operating normally."
        patch = "No action needed – vehicle is normal."
    else:
        explanation = "Unknown attack type."
        patch = "No patch suggestion available."

    return f"Attack Type: {attack_type}\nExplanation: {explanation}\nSuggested Patch: {patch}"

########################################
# Load & Preprocess CAN data
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
                data_bytes = parts[7:7 + dlc]
                byte_values = [int(b, 16) for b in data_bytes]

                while len(byte_values) < 8:
                    byte_values.append(0)

                # ✅ Input prompt contains only CAN data
                prompt = f"CAN ID: {can_id}, DLC: {dlc}, Data: {byte_values}"

                # ✅ Target contains attack type, explanation, patch
                response = get_patch_and_explanation_for_attack(attack_type, byte_values)

                data.append({"input_text": prompt, "target_text": response})
            except Exception as e:
                continue

    return data

# Load and preprocess data
data = load_and_preprocess_data(dataset_files)
if not data:
    print("⚠ No valid lines parsed. Exiting.")
    exit()

# Convert to Hugging Face dataset
hf_dataset = Dataset.from_dict({
    "input_text": [item["input_text"] for item in data],
    "target_text": [item["target_text"] for item in data]
})

# Shuffle and use only the first 5000 samples
hf_dataset = hf_dataset.shuffle(seed=42).select(range(min(5000, len(hf_dataset))))

########################################
# Load tokenizer and model
########################################
print("🔧 Loading DistilGPT2...")
tokenizer = GPT2TokenizerFast.from_pretrained("distilgpt2")
tokenizer.pad_token = tokenizer.eos_token  # Prevent padding errors

model = GPT2LMHeadModel.from_pretrained("distilgpt2")
model.resize_token_embeddings(len(tokenizer))

########################################
# Tokenization
########################################
def tokenize_function(example):
    input_ids = tokenizer(
        example["input_text"] + "\n" + example["target_text"],
        padding="max_length",
        truncation=True,
        max_length=256
    )
    return input_ids

print("🔧 Tokenizing dataset...")
tokenized_dataset = hf_dataset.map(tokenize_function, batched=False, remove_columns=["input_text", "target_text"])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

########################################
# Training configuration
########################################
base_path = "./"  # Change this as needed

training_args = TrainingArguments(
    output_dir=os.path.join(base_path, "model/distilgpt2_model"),
    num_train_epochs=3,
    per_device_train_batch_size=8,
    save_steps=500,
    logging_steps=50,
    save_total_limit=2,
    weight_decay=0.01,
    warmup_steps=100,
    learning_rate=5e-5,
    logging_dir=os.path.join(base_path, "logs"),
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

########################################
# Train and Save
########################################
print("🚀 Starting fine-tuning...")
trainer.train()

save_path = os.path.join(base_path, "model/fine_tuned_distilgpt2")
trainer.save_model(save_path)
tokenizer.save_pretrained(save_path)

print("✅ Fine-tuning complete!")