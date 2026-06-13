import requests
import json
from config import PROVIDERS, MAX_TOKENS, MAX_HISTORY_MESSAGES, SYSTEM_PROMPT
from memory import save_history
from tools import run_python_code, web_search

TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "run_python_code",
            "description": "Выполняет Python-код и возвращает вывод (stdout/stderr). Используй для проверки правильности кода.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python-код для выполнения"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Ищет актуальную информацию в интернете. Используй для вопросов о текущих событиях, версиях ПО, новостях или фактах, которые могут быть устаревшими в твоих знаниях.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Поисковый запрос"}
                },
                "required": ["query"]
            }
        }
    }
]

AVAILABLE_TOOLS = {"run_python_code": run_python_code, "web_search": web_search}

def _call_provider(provider, messages):
    headers = {
        "Authorization": f"Bearer {provider['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": provider["model"],
        "max_tokens": MAX_TOKENS,
        "messages": messages,
        "tools": TOOLS_SPEC
    }
    response = requests.post(provider["url"], headers=headers, json=payload, timeout=60)
    return response

def _call_api(messages):
    last_error = None
    for provider in PROVIDERS:
        if not provider["api_key"]:
            continue
        try:
            response = _call_provider(provider, messages)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429:
                last_error = f"{provider['name']}: лимит запросов (429)"
                continue
            last_error = f"{provider['name']}: ошибка {response.status_code}: {response.text[:200]}"
            continue
        except Exception as e:
            last_error = f"{provider['name']}: исключение {e}"
            continue
    raise RuntimeError(f"Все провайдеры недоступны. Последняя ошибка: {last_error}")

def ask(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    trimmed_history = history[-MAX_HISTORY_MESSAGES:]
    messages.extend(trimmed_history)
    messages.append({"role": "user", "content": user_message})

    try:
        data = _call_api(messages)
    except RuntimeError as e:
        return str(e)

    choice = data["choices"][0]["message"]

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
        try:
            data = _call_api(messages)
            choice = data["choices"][0]["message"]
        except RuntimeError as e:
            return str(e)

    reply = choice["content"]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    save_history(history)

    return reply
