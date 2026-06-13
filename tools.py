import subprocess

def run_python_code(code: str) -> str:
    """Выполняет Python-код и возвращает результат (stdout/stderr)."""
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr
        return output.strip() if output.strip() else "(нет вывода)"
    except subprocess.TimeoutExpired:
        return "ОШИБКА: превышено время выполнения (10 сек)"
    except Exception as e:
        return f"ОШИБКА: {e}"

import os
import requests as _requests

def web_search(query: str) -> str:
    """Ищет актуальную информацию в интернете по запросу."""
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return "Веб-поиск недоступен: нет API-ключа Tavily"
    try:
        response = _requests.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": 3},
            timeout=15
        )
        if response.status_code != 200:
            return f"Ошибка поиска: {response.status_code}"
        data = response.json()
        results = data.get("results", [])
        if not results:
            return "Ничего не найдено"
        output = []
        for r in results:
            output.append(f"- {r.get('title', '')}: {r.get('content', '')[:200]}")
        return "\n".join(output)
    except Exception as e:
        return f"Ошибка поиска: {e}"
