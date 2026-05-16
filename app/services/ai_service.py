import os
import requests
from dotenv import load_dotenv
from app.services.Teach_Ai_DataBase import get_database_schema

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"

HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}
# ----------------------------
# 2. AI FUNCTION
# ----------------------------
def ask_ai(question: str):

    schema = get_database_schema()

    payload = {
        "model": "deepseek-ai/DeepSeek-V4-Pro:novita",
        "messages": [
            {
                "role": "system",
                "content": f"""
You are an expert SQL generator.

RULES:
- Only return SQL
- No explanation
- No markdown
- Use ONLY this database schema:

{schema}
"""
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "temperature": 0
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    data = response.json()

    if "choices" in data:
        return data["choices"][0]["message"]["content"]

    return data


# ----------------------------
# TEST
# ----------------------------
if __name__ == "__main__":

    result = ask_ai("Get all users who placed orders")

    print("\nFINAL RESULT:")
    print(result)