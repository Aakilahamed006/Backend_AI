import os
import requests
from dotenv import load_dotenv

from app.services.Teach_Ai_DataBase import (
    get_database_schema
)

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"

HF_TOKEN = os.getenv("HF_TOKEN_1")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


# ----------------------------
# AI FUNCTION
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
- Return ONLY SQL
- No explanation
- No markdown
- No comments

IMPORTANT:
- ALWAYS generate parameterized SQL
- NEVER hardcode values directly

GOOD EXAMPLE:
INSERT INTO users (name, age)
VALUES (:name, :age)

BAD EXAMPLE:
INSERT INTO users (name, age)
VALUES ('Aakil', 23)

FOR SELECT:
GOOD:
SELECT name FROM users
WHERE age > :age

DATABASE SCHEMA:
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

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    print("\nSTATUS:")
    print(response.status_code)

    print("\nRAW RESPONSE:")
    print(response.text)

    data = response.json()

    if "choices" in data:

        sql_query = data["choices"][0]["message"]["content"]

        print("\nGENERATED SQL:")
        print(sql_query)

        return sql_query

    return {
        "error": data
    }


# ----------------------------
# TEST
# ----------------------------
if __name__ == "__main__":

    result = ask_ai(
        "Add a new user [name=Zorrow,age=35]"
    )

    print("\nFINAL RESULT:")
    print(result)