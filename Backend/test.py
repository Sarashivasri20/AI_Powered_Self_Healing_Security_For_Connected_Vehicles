from transformers import GPT2TokenizerFast, GPT2LMHeadModel

# Load fine-tuned model and tokenizer
model_path = "./model/fine_tuned_distilgpt2"
tokenizer = GPT2TokenizerFast.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)

# Input prompt
input_text = f"""CAN ID: 450 , DLC: 8, Data: [200, 233, 200, 250, 17, 23, 120, 160]"""

# Tokenize
inputs = tokenizer(input_text, return_tensors="pt")

# Generate response
outputs = model.generate(
    **inputs,
    max_length=256,
    do_sample=True,
    top_k=50,
    temperature=0.9,
    repetition_penalty=1.2,
    pad_token_id=tokenizer.eos_token_id
)

# Decode and print
output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("📥 Input:", input_text)
print("📤 Output:\n", output_text)