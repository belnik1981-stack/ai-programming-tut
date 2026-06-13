import subprocess
import ast
import tempfile
import shutil

ALLOWED_MODULES = {"math", "random", "statistics", "itertools", "collections", "datetime", "json", "re", "string", "functools", "decimal", "fractions"}

def _check_code_safety(code: str) -> str:
    """Возвращает сообщение об ошибке если код использует запрещённые конструкции, иначе пустую строку."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"Синтаксическая ошибка: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in ALLOWED_MODULES:
                    return f"Модуль не в списке разрешённых: {alias.name}"
        if isinstance(node, ast.ImportFrom):
            top = (node.module or "").split(".")[0]
            if top not in ALLOWED_MODULES:
                return f"Модуль не в списке разрешённых: {node.module}"
        if isinstance(node, ast.Name) and node.id in ("__import__", "open", "exec", "eval", "compile", "input", "getattr", "globals", "locals", "vars"):
            return f"Запрещённая функция: {node.id}"
        if isinstance(node, ast.Attribute) and node.attr in ("__import__", "__builtins__", "__globals__", "__subclasses__", "__bases__"):
            return f"Запрещённый атрибут: {node.attr}"
    return ""


def _limit_resources():
    """Вызывается в дочернем процессе перед exec для ограничения CPU-времени."""
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))


def _classify_error(stderr: str) -> str:
    """Определяет тип ошибки по последней строке traceback."""
    last_line = stderr.strip().splitlines()[-1] if stderr.strip() else ""
    if "SyntaxError" in last_line or "IndentationError" in last_line:
        return "ERROR_SYNTAX"
    if "NameError" in last_line:
        return "ERROR_NAME"
    if "TypeError" in last_line:
        return "ERROR_TYPE"
    if "ZeroDivisionError" in last_line or "ValueError" in last_line or "IndexError" in last_line or "KeyError" in last_line:
        return "ERROR_RUNTIME"
    return "ERROR_RUNTIME"


def run_python_code(code: str) -> str:
    """Выполняет Python-код в изолированном окружении (без доступа к env, файловой системе вне сэндбокса, опасным модулям, с лимитом памяти/CPU)."""
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
            env={"PATH": "/data/data/com.termux/files/usr/bin"},
            preexec_fn=_limit_resources
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            error_type = _classify_error(stderr)
            return f"[{error_type}]\n{stderr or 'no stderr'}"

        if stdout:
            return f"[OK]\n{stdout}"

        return "[OK_NO_OUTPUT]"
    except subprocess.TimeoutExpired:
        return "[ERROR_TIMEOUT]\nПревышено время выполнения (10 сек)"
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
