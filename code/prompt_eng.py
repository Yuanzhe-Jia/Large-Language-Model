import json
from text_generation import Client
from transformers import AutoTokenizer

model_id = "TechxGenus/Meta-Llama-3-70B-Instruct-AWQ"
tokenizer = AutoTokenizer.from_pretrained(model_id)

messages = [
    {
        "role": "system",
        "content": """
            You will be given a content. 
            The content describes a period of continuous user behavior on the app that includes 2 critical events: the initial event and the complete event. 
            First, understand the above content, and come out a description for the initial event and the complete event, respectively. Each description should be less than 20 words.
            Second, base on the description, come out a straightforward and readable (not camel case or snake case) name for each event. Each event name should be less than 4 words.
            In the end, only output a JSON in your response that contains 2 objects: "initial_event" and "complete_event" with "event_description" and "event_name" keys.
        """,
    },
    {
        "role": "user",
        "content": "search to video play"
    },
]

prompt = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)

# Llama 3 70B
HOST = "http://...:9008"
client = Client(HOST, timeout=60)
result = []
for c in client.generate_stream(
    prompt, max_new_tokens=1024, stop_sequences=[tokenizer.eos_token, "<|eot_id|>"]
):
    result.append(c.token.text)

print(''.join(result))
