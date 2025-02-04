from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
import json

model = "tiiuae/falcon-7b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto",
)

def invoke(input_text):
    try:
        input_json = json.loads(input_text)
    except:
        sequences = pipeline(
            input_text,
            max_length=50,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
        )
        result = ""
        for seq in sequences:
            result += seq['generated_text']
        return result
    try:
        input_json = json.loads(input_text)
        if 'prompt' not in input_json:
            sequences = pipeline(
                input_text,
                max_length=50,
                do_sample=True,
                top_k=10,
                num_return_sequences=1,
                eos_token_id=tokenizer.eos_token_id,
            )
        else:
            prompt = input_json['prompt']
            max_length = int(input_json['max_length']) if 'max_length' in input_json else 50
            top_k = int(input_json['top_k']) if 'top_k' in input_json else 10
            do_sample = input_json['do_sample'].lower()=="true" if 'do_sample' in input_json else True
            num_return_sequences = int(input_json['num_return_sequences']) if 'num_return_sequences' in input_json else 1

            sequences = pipeline(
                prompt,
                max_length=max_length,
                do_sample=do_sample,
                top_k=top_k,
                num_return_sequences=num_return_sequences,
                eos_token_id=tokenizer.eos_token_id,
            )
        result = ""
        for seq in sequences:
            result += seq['generated_text']
        return result
    except Exception as e:
        result = "Error: " + str(e)
        return result
