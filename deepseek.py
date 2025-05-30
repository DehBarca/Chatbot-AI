from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not API_KEY:
    raise ValueError("DEEP_API_KEY not found in .env file.")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= API_KEY,
)

completion = client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=[
                    {
                "role": "user",
                "content": "What is the meaning of life?"
                    }
                ]
            )
response = {"text": completion.choices[0].message.content}
print(response["text"])
