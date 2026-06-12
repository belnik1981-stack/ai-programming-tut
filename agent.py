import requests
import json
from config import API_KEY, API_URL, MODEL, MAX_TOKENS, SYSTEM_PROMPT
from memory import load_history, save_history

def ask(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": messages
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        return f"ОШИБКА {response.status_code}: {response.text}"

    data = response.json()
    reply = data["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    save_history(history)

    return reply
