import os

SYSTEM_PROMPT = """Ты — персональный наставник по программированию.
Объясняй на русском или украинском (как пишет пользователь).
Фокус: Python, JavaScript, основы цифровой безопасности (пароли, фишинг, VPN, шифрование).
Будь точным и математически честным, избегай излишних хеджей и воды.
Если пользователь делает ошибку — прямо указывай и объясняй почему."""

HISTORY_FILE = "data/history.json"
MAX_TOKENS = 1024
MAX_HISTORY_MESSAGES = 4

PROVIDERS = [
    {
        "name": "openrouter",
        "api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "meta-llama/llama-3.3-70b-instruct:free"
    },
    {
        "name": "groq",
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile"
    },
    {
        "name": "gemini",
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model": "gemini-2.5-flash"
    }
]
