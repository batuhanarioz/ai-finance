import os
from dotenv import load_dotenv
from backend.agents.orchestrator import app
from langchain_core.messages import HumanMessage

load_dotenv()

def run_fin_agent():
    print("🏦 FinAgent AI Operasyon Merkezi Başlatıldı...")
    print("------------------------------------------")
    
    # Başlangıç State'i
    config = {"configurable": {"thread_id": "1"}}
    initial_state = {
        "messages": [],
        "user_info": {"account_id": "TR001", "credit_score": 1850},
        "is_risk_cleared": False
    }

    while True:
        user_input = input("\n👤 Siz: ")
        if user_input.lower() in ["exit", "quit", "çıkış"]:
            break

        # Mesajı grafiğe gönder
        events = app.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config,
            stream_mode="values"
        )

        for event in events:
            if "messages" in event:
                last_msg = event["messages"][-1]
                if last_msg.type == "assistant":
                    print(f"\n🤖 FinAgent: {last_msg.content}")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Hata: .env dosyasına OPENAI_API_KEY eklemelisiniz!")
    else:
        run_fin_agent()
