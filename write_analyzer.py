content = r'''import json
import os
from collections import Counter

ISSUES_FILE = "data/issues.json"


def analyze():
    if not os.path.exists(ISSUES_FILE):
        print("Нет данных issues.json — пока всё чисто.")
        return

    with open(ISSUES_FILE, "r", encoding="utf-8") as f:
        issues = json.load(f)

    if not issues:
        print("issues.json пуст.")
        return

    print(f"Всего записей: {len(issues)}\n")

    by_type = Counter(i["type"] for i in issues)
    print("По типу:")
    for t, count in by_type.items():
        print(f"  {t}: {count}")

    by_provider = Counter(i["details"].get("provider", "?") for i in issues)
    print("\nПо провайдеру:")
    for p, count in by_provider.items():
        print(f"  {p}: {count}")

    print("\nРекомендации:")
    if by_type.get("rate_limit", 0) > 5:
        print("  - Много rate_limit: рассмотри увеличение пауз между запросами или платный tier.")
    for i in issues:
        if i["type"] == "api_error" and "tool_use_failed" in i["details"].get("body", ""):
            print("  - Найдены ошибки tool_use_failed: проверь MAX_TOKENS (должен быть >= 1024).")
            break


if __name__ == "__main__":
    analyze()
'''

with open("analyze_issues.py", "w", encoding="utf-8") as f:
    f.write(content)

print("analyze_issues.py written")
