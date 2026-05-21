import os
import requests

from dotenv import load_dotenv

from app.services.schema_service import get_database_schema

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"

HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def correct_sql(
    question: str,
    wrong_sql: str,
    db_error: str
):

    schema = get_database_schema()

    payload = {

        "model": "deepseek-ai/DeepSeek-V4-Pro:novita",

        "messages": [

            {
                "role": "system",

                "content": f"""
You are an SQL correction engine.

RULES:
- Fix SQL queries
- Return ONLY corrected SQL
- No explanation
- No markdown
- Only SELECT queries

DATABASE SCHEMA:

{schema}
"""
            },

            {
                "role": "user",

                "content": f"""
QUESTION:
{question}

BROKEN SQL:
{wrong_sql}

DATABASE ERROR:
{db_error}

Fix the query.
"""
            }
        ],

        "temperature": 0
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    data = response.json()

    print("CORRECTION RESPONSE:", data)

    if "choices" in data:

        return data["choices"][0]["message"]["content"]

    return None