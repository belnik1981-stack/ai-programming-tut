import requests
import json
import re
from config import PROVIDERS, MAX_TOKENS, MAX_HISTORY_MESSAGES, SYSTEM_PROMPT
from memory import save_history, log_issue
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
            "description": "Ищет актуальную информацию в интернете. Используй для вопросов о текущих событиях, версиях ПО, новостях, погоде или фактах, которые могут быть устаревшими.",
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

TOOL_TRIGGER_WORDS = [
    "посчитай", "выполни", "запусти", "код", "проверь",
    "найди", "поиск", "найди в интернете", "используй поиск",
    "погода", "сегодня", "сейчас", "последняя версия", "новост",
    "актуальн", "текущ", "вышла", "выйдет"
]

def _needs_tools(user_message):
    text = user_message.lower()
    return any(word in text for word in TOOL_TRIGGER_WORDS)


def _parse_text_tool_call(text):
    """Парсит формат <function(name){args}</function>, если модель вернула tool call как текст."""
    match = re.search(r'<function\(([a-zA-Z_]+)\)(\{.*?\})</function>', text)
    if match:
        name = match.group(1)
        args_str = match.group(2)
        try:
            args = json.loads(args_str)
            return name, args
        except json.JSONDecodeError:
            return None, None
    return None, None


def _call_provider(provider, messages, use_tools=True):
    headers = {
        "Authorization": f"Bearer {provider['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": provider["model"],
        "max_tokens": MAX_TOKENS,
        "messages": messages
    }
    if use_tools:
        payload["tools"] = TOOLS_SPEC
    response = requests.post(provider["url"], headers=headers, json=payload, timeout=60)
    return response


def _call_api(messages, use_tools=True):
    errors = []
    for provider in PROVIDERS:
        if not provider["api_key"]:
            continue
        try:
            response = _call_provider(provider, messages, use_tools)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429 or response.status_code >= 500:
                errors.append(f"{provider['name']}: {response.status_code}")
                log_issue("rate_limit_or_server_error", {"provider": provider['name'], "status": response.status_code})
                continue
            # 4xx (кроме 429) - проблема в самом запросе, переключение провайдера не поможет
            log_issue("request_error", {"provider": provider['name'], "status": response.status_code, "body": response.text[:200]})
            raise RuntimeError(f"{provider['name']}: ошибка запроса {response.status_code}: {response.text[:200]}")
        except Exception as e:
            errors.append(f"{provider['name']}: exc {e}")
            continue
    raise RuntimeError(f"Все провайдеры недоступны. Ошибки: {errors}")


def ask(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    trimmed_history = history[-MAX_HISTORY_MESSAGES:]
    messages.extend(trimmed_history)
    messages.append({"role": "user", "content": user_message})

    use_tools = _needs_tools(user_message)

    try:
        data = _call_api(messages, use_tools)
    except RuntimeError as e:
        return str(e)

    choice = data["choices"][0]["message"]

    if not choice.get("tool_calls") and choice.get("content"):
        fn_name, fn_args = _parse_text_tool_call(choice["content"])
        if fn_name and fn_name in AVAILABLE_TOOLS:
            result = AVAILABLE_TOOLS[fn_name](**fn_args)
            messages.append({"role": "assistant", "content": choice["content"]})
            messages.append({"role": "user", "content": f"Результат поиска: {result}\n\nДай содержательный ответ на основе этих данных, на русском или украинском."})
            try:
                data = _call_api(messages)
                choice = data["choices"][0]["message"]
            except RuntimeError as e:
                return str(e)

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
