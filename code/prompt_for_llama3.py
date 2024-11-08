import json
from text_generation import Client
from transformers import AutoTokenizer

model_id = "TechxGenus/Meta-Llama-3-70B-Instruct-AWQ"
tokenizer = AutoTokenizer.from_pretrained(model_id)


messages = [
    {
        "role": "system",
        "content": """
            You'll be given a short sentence trying to describe two consecutive events of a user when playing with an App.
            First, please understand the sentence and extract these two events, please come out a comprehensive description of each event.
            Then, base on the description, please also come out a straightforward and readable(not camel case or snake case) name for each event.
            In then end, put your result into a JSON which has 2 JSON objects: "start_event" and "end_event" with "name" and "description" keys.
            Your output should be just a JSON object
        """,
    },
    {
        "role": "user",
        "content": "'search' to 'video play'"
    },
]

prompt = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)


# Llama 3 70B
HOST = "9008"
client = Client(HOST, timeout=60)
result = []
for c in client.generate_stream(
    prompt, max_new_tokens=1024, stop_sequences=[tokenizer.eos_token, "<|eot_id|>"]
):
    result.append(c.token.text)

print(''.join(result))