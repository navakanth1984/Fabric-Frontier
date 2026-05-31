import sqlite3
from pathlib import Path
from collections import Counter

DB_PATH = Path("c:/Users/navka/navakanth001/nthdimensionacademy/intent_tracking.db")

def analyze_buyer_intent():
    if not DB_PATH.exists():
        print("No interaction data found yet.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT message FROM interactions WHERE role='user'")
    user_messages = [row[0] for row in c.fetchall()]
    conn.close()

    print("--- BUYER INTENT ANALYSIS (CRM Step 6) ---")
    print(f"Total Interactions: {len(user_messages)}")
    
    if len(user_messages) > 0:
        print("\nTop Inquiries:")
        keywords = ['Fabric', 'Azure', 'DP-600', 'Medallion', 'Meeting', 'Training']
        for kw in keywords:
            count = sum(1 for msg in user_messages if kw.lower() in msg.lower())
            print(f"- {kw}: {count} hits")
            
        print("\nRaw Insights for SEO Strategy:")
        for msg in user_messages[-5:]:
            print(f"  > \"{msg}\"")
    else:
        print("Waiting for more user interactions...")

if __name__ == "__main__":
    analyze_buyer_intent()
