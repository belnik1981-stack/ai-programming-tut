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
