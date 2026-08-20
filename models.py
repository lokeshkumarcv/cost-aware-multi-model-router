import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")

client = Groq(api_key=api_key)

LOW_COST_MODEL = "openai/gpt-oss-20b"
HIGH_COST_MODEL = "openai/gpt-oss-120b"


def call_model(model, prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return {
        "text": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }


def call_low_cost_model(prompt):
    return call_model(LOW_COST_MODEL, prompt)


def call_high_cost_model(prompt):
    return call_model(HIGH_COST_MODEL, prompt)