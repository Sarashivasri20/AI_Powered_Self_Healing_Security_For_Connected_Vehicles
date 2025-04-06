from transformers import GPT2TokenizerFast, GPT2LMHeadModel
import re

# Load fine-tuned model and tokenizer
model_path = "./model/fine_tuned_distilgpt2"
tokenizer = GPT2TokenizerFast.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)


def parse_gpt_output(output_text):
    """
    Clean and parse GPT output: remove echoed input, extract key fields robustly.
    """
    # Trim everything before "Attack Type"
    start_index = re.search(r"(?i)attack\s*type\s*:", output_text)
    if start_index:
        output_text = output_text[start_index.start():]
    else:
        return {
            "attack_type": "Unknown",
            "explanation": "No explanation available.",
            "patch": "No patch suggested."
        }

    # Extract fields as before
    attack_type_match = re.search(r"(?i)attack\s*type\s*:\s*(.+?)(?=\n|$)", output_text)
    explanation_match = re.search(r"(?i)explanation\s*:\s*(.+?)(?=\n|suggested\s*patch\s*:|$)", output_text, re.DOTALL)
    patch_match = re.search(r"(?i)suggested\s*patch\s*:\s*(.+?)(?=\n|$)", output_text, re.DOTALL)

    return {
        "attack_type": attack_type_match.group(1).strip() if attack_type_match else "Unknown",
        "explanation": explanation_match.group(1).strip() if explanation_match else "No explanation available.",
        "patch": patch_match.group(1).strip() if patch_match else "No patch suggested."
    }


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

# Parse the output
parsed_output = parse_gpt_output(output_text)
print("Parsed Output:", parsed_output)


print("📥 Input:", input_text)
print("📤 Output:\n", output_text)