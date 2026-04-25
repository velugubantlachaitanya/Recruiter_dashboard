import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")
print(f"Testing key starting with: {key[:15]}... (length: {len(key)})")

client = anthropic.Anthropic(api_key=key)
try:
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=10,
        messages=[{"role": "user", "content": "hi"}]
    )
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
