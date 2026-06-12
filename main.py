from agent import ask
from memory import load_history, clear_history

def main():
    print("AI-наставник по программированию. Команды: /clear — очистить память, /exit — выход")
    history = load_history()
    print(f"Загружено сообщений из истории: {len(history)}")

    while True:
        user_input = input("\nТы: ").strip()
        if not user_input:
            continue
        if user_input == "/exit":
            break
        if user_input == "/clear":
            clear_history()
            history = []
            print("История очищена.")
            continue

        reply = ask(user_input, history)
        print(f"\nАгент: {reply}")

if __name__ == "__main__":
    main()
