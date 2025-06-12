import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in .env file.")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= DEEPSEEK_KEY,
)


def obtenerMensaje(model_id, message, archivo):
    completion = client.chat.completions.create(
    model= model_id,
    messages=[
            {
        "role": "user",
        "content": message
            }
        ]
    )
    response = {"text": completion.choices[0].message.content}
    return response["text"]