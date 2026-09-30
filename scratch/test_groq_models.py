import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompt = "Respond strictly in JSON: {\"status\": \"ok\"}"

for m in ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
    try:
        resp = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        print(f"{m}: SUCCESS -> {resp.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"{m}: Error {e}")
