import subprocess
import ast
import tempfile
import shutil

BLOCKED_MODULES = {"os", "subprocess", "socket", "shutil", "pathlib", "sys", "ctypes"}

def _check_code_safety(code: str) -> str:
    """Возвращает сообщение об ошибке если код использует запрещённые модули, иначе пустую строку."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"Синтаксическая ошибка: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in BLOCKED_MODULES:
                    return f"Запрещённый модуль: {alias.name}"
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in BLOCKED_MODULES:
                return f"Запрещённый модуль: {node.module}"
        if isinstance(node, ast.Name) and node.id == "__import__":
            return "Запрещена прямая функция __import__"
    return ""


def run_python_code(code: str) -> str:
    """Выполняет Python-код в изолированном окружении (без доступа к env, файловой системе вне сэндбокса и опасным модулям)."""
    safety_issue = _check_code_safety(code)
    if safety_issue:
        return f"ОТКАЗ: код не выполнен. {safety_issue}"

    sandbox_dir = tempfile.mkdtemp(prefix="sandbox_")
    try:
        result = subprocess.run(
            ["python3", "-I", "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=sandbox_dir,
            env={"PATH": "/data/data/com.termux/files/usr/bin"}
        )
        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr
        return output.strip() if output.strip() else "(нет вывода)"
    except subprocess.TimeoutExpired:
        return "ОШИБКА: превышено время выполнения (10 сек)"
    except Exception as e:
        return f"ОШИБКА: {e}"
    finally:
        shutil.rmtree(sandbox_dir, ignore_errors=True)

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
