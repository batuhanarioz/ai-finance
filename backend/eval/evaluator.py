import os
import json
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance, context_precision
from datasets import Dataset
from backend.core.rag_manager import rag_engine
from langchain_openai import ChatOpenAI
from backend.core.config import settings

# Evaluation LLM
eval_llm = ChatOpenAI(model="gpt-4o", temperature=0)

def run_evaluation():
    """RAGAS kullanarak sistemi değerlendirir."""
    
    # 1. Test Seti Oluştur (Altın, Faiz, Mevduat soruları)
    test_questions = [
        "Altın hesabı açmak için alt limit nedir?",
        "Kur korumalı mevduatın avantajı nedir?",
        "Kredi kartı nakit avans faiz oranı nedir?"
    ]
    
    ground_truths = [
        "Altın hesabı için alt limit 1 gramdır.",
        "Kur farkı koruması ve faiz getirisi sağlar.",
        "Nakit avans faiz oranı aylık %4.42'dir."
    ]

    results = []
    
    for q in test_questions:
        # RAG sisteminden cevap ve context al
        context = rag_engine.search(q, k=2)
        # Basit bir cevap üretimi (eval için)
        response = eval_llm.invoke(f"Context: {context}\nQuestion: {q}").content
        
        results.append({
            "question": q,
            "answer": response,
            "contexts": [context],
            "ground_truth": ground_truths[test_questions.index(q)]
        })

    # 2. Dataset Formatına Çevir
    dataset = Dataset.from_list(results)
    
    # 3. Değerlendir
    score = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevance, context_precision],
        llm=eval_llm
    )
    
    # 4. Sonuçları Kaydet
    report_path = "backend/data/eval_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(score, f, indent=4)
    
    return score

if __name__ == "__main__":
    print("RAGAS Değerlendirmesi başlatılıyor...")
    report = run_evaluation()
    print(f"Değerlendirme tamamlandı: {report}")
