import requests
import json
from config import API_KEY, API_URL, MODEL, MAX_TOKENS, SYSTEM_PROMPT
from memory import save_history
from tools import run_python_code

TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "run_python_code",
            "description": "Выполняет Python-код и возвращает вывод (stdout/stderr). Используй для проверки правильности кода.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python-код для выполнения"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

AVAILABLE_TOOLS = {
    "run_python_code": run_python_code
}

def _call_api(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
        "tools": TOOLS_SPEC
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"ОШИБКА {response.status_code}: {response.text}")
    return response.json()

def ask(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    data = _call_api(messages)
    choice = data["choices"][0]["message"]

    # Если модель хочет вызвать tool
    if choice.get("tool_calls"):
        messages.append(choice)
        for tool_call in choice["tool_calls"]:
            fn_name = tool_call["function"]["name"]
            fn_args = json.loads(tool_call["function"]["arguments"])
            fn = AVAILABLE_TOOLS.get(fn_name)
            result = fn(**fn_args) if fn else f"Неизвестный tool: {fn_name}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })

        # Второй вызов — модель формулирует финальный ответ с учётом результата tool
        data = _call_api(messages)
        choice = data["choices"][0]["message"]

    reply = choice["content"]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    save_history(history)

    return reply
