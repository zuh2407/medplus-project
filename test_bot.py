import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from chatbot_api.app.health_bot import HealthBot

def test():
    bot = HealthBot()
    
    queries = [
        "symptoms of fever",
        "symptoms of flu",
        "what is acetaminophen"
    ]
    
    with open("bot_result.txt", "w", encoding="utf-8") as f:
        for q in queries:
            f.write(f"\nQUERY: {q}\n")
            f.write("-" * 20 + "\n")
            res = bot.search(q, top_k=1)
            f.write(str(res) + "\n")
            f.write("=" * 40 + "\n")

if __name__ == "__main__":
    test()
