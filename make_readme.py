content = '''# AI Programming Tutor / AI-наставник по программированию

Lightweight self-hosted AI agent for learning programming and digital security. Runs in Termux on Android using raw HTTP calls (no heavy SDK).

Легкий AI-агент-наставник для изучения программирования и цифровой безопасности. Работает в Termux на Android только через requests.

## Architecture / Архитектура

- config.py - API keys, model settings, system prompt
- memory.py - persistent conversation history (JSON)
- tools.py - function-calling tools
- agent.py - core loop: API calls + tool execution
- main.py - CLI interface

## Features / Возможности

- Persistent memory across sessions
- Function calling (agent executes Python code to verify answers)
- Bilingual system prompt (RU/UK)
- Zero heavy dependencies - runs on Android/Termux
- Provider-agnostic - currently Groq API, swappable to any OpenAI-compatible endpoint

## Setup

pip install requests --break-system-packages
export GROQ_API_KEY=your_key_here
python main.py

## Roadmap

- Web UI (Flask)
- Glossary tool
- Risk-management module for trading bot (separate project)
'''

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("README.md created")
