from backend.core.rag_manager import rag_engine
import os

def run_evaluation():
    print("🧪 RAG Doğruluk Testi Başlatılıyor...")
    
    test_queries = [
        {"q": "Mevduat hesabı açmak için alt limit nedir?", "expected": "10.000 TL"},
        {"q": "FAST limiti ne kadar?", "expected": "50.000 TL"},
        {"q": "Konut kredisi vadesi kaç ay?", "expected": "120 ay"}
    ]
    
    if not os.path.exists("backend/data"):
        print("❌ Hata: Test dökümanları bulunamadı.")
        return

    rag_engine.load_documents("backend/data")
    
    score = 0
    for test in test_queries:
        result = rag_engine.query(test["q"])
        if test["expected"] in result:
            print(f"✅ BAŞARILI | Soru: {test['q']}")
            score += 1
        else:
            print(f"❌ BAŞARISIZ | Soru: {test['q']} | Beklenen: {test['expected']}")

    print(f"\n📊 Test Sonucu: {score}/{len(test_queries)} Doğruluk")

if __name__ == "__main__":
    run_evaluation()
