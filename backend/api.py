from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from backend.core.rag_manager import rag_engine
import shutil
from pydantic import BaseModel
from typing import Optional
import json
import asyncio
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from backend.agents.orchestrator import app as langgraph_app
from langchain_core.messages import HumanMessage
from backend.core.security import security_audit
from backend.mcp_server.bank_server import MOCK_ACCOUNTS
from prometheus_fastapi_instrumentator import Instrumentator

api = FastAPI(title="FinAgent Enterprise API")
Instrumentator().instrument(api).expose(api)

@api.get("/accounts")
async def get_accounts():
    """Tüm hesapları döner."""
    return MOCK_ACCOUNTS

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str = "TR001"
    target_agent: Optional[str] = None

from backend.core.logger import logger

@api.get("/health")
async def health_check():
    """Sistemin ayakta olduğunu ve servislerin durumunu döner."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "rag": "online",
            "langgraph": "online",
            "security": "active"
        }
    }

@api.get("/audit-logs")
async def get_audit_logs():
    """Denetim kayıtlarını döner."""
    logs = []
    try:
        with open("backend/data/audit_logs.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                logs.append(json.loads(line))
        return logs[::-1] # Son kayıtlar üstte
    except FileNotFoundError:
        return []

@api.get("/security-stats")
async def get_security_stats():
    """Güvenlik motoru istatistiklerini döner."""
    try:
        with open("backend/data/audit_logs.jsonl", "r", encoding="utf-8") as f:
            all_logs = [json.loads(line) for line in f]
        
        threats = len([l for l in all_logs if l["action"] == "SECURITY_THREAT_DETECTED"])
        ai_res = len([l for l in all_logs if l["action"] == "AI_RESPONSE_GENERATED"])
        risk_checks = len([l for l in all_logs if l["action"] == "RISK_ANALYSIS"])
        
        return {
            "total_ai_responses": ai_res,
            "threats_blocked": threats,
            "risk_checks_performed": risk_checks,
            "uptime_status": "Operational"
        }
    except Exception:
        return {"total_ai_responses": 0, "threats_blocked": 0, "risk_checks_performed": 0, "uptime_status": "Operational"}

@api.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # 1. Rate Limiting Kontrolü
    if security_audit.is_rate_limited(req.user_id):
        logger.error(f"Rate limit exceeded for user: {req.user_id}")
        raise HTTPException(status_code=429, detail="Çok fazla istek gönderildi. Lütfen bekleyin.")

    # 2. Tehdit Taraması
    if security_audit.check_threats(req.message):
        logger.audit("SECURITY_THREAT_DETECTED", req.user_id, {"input": req.message})
        raise HTTPException(status_code=400, detail="Güvenlik politikası ihlali tespit edildi.")

    async def event_generator():
        config = {"configurable": {"thread_id": req.user_id}}
        
        # 3. PII Maskeleme ve Loglama
        clean_msg = security_audit.mask_pii(req.message)
        logger.info(f"Chat request started", extra={"user_id": req.user_id})
        
        # İlk 'düşünce' mesajını gönder
        yield f"data: {json.dumps({'content': '', 'sender': 'system', 'thought': 'İstek analiz ediliyor...', 'next_node': 'supervisor'})}\n\n"

        async for event in langgraph_app.astream(
            {
                "messages": [HumanMessage(content=clean_msg)],
                "next_step": req.target_agent,
                "user_info": {"account_id": req.user_id, "name": "Batuhan Arıöz", "credit_score": 1850}
            },
            config,
            stream_mode="values"
        ):
            if event and "messages" in event:
                last_message = event["messages"][-1]
                
                # İnsan mesajlarını stream içerisinde geri gönderme (kullanıcı zaten kendi yazdığını biliyor)
                if last_message.type == "human":
                    continue

                # Düşünce (thought) belirleme
                node_thoughts = {
                    "supervisor": "İstek analiz ediliyor...",
                    "risk_agent": "Güvenlik denetimi yapılıyor...",
                    "product_agent": "Bilgi bankası taranıyor...",
                    "transactional_agent": "Banka sistemine erişiliyor...",
                    "verifier": "Cevap doğrulanıyor...",
                    "human_approval": "Onay bekleniyor..."
                }
                
                data = {
                    "content": last_message.content if hasattr(last_message, 'content') else "",
                    "sender": last_message.type if hasattr(last_message, 'type') else "system",
                    "thought": node_thoughts.get(event.get("next_step", ""), "İşleniyor..."),
                    "next_node": event.get("next_step", "End")
                }
                
                # 4. Audit Log Kaydı
                if data["sender"] == "ai":
                    logger.audit("AI_RESPONSE_GENERATED", req.user_id, {"node": data["next_node"]})

                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(0.1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@api.get("/eval-report")
async def get_eval_report():
    """RAGAS değerlendirme raporunu döner."""
    try:
        with open("backend/data/eval_report.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"message": "Değerlendirme raporu henüz oluşturulmadı.", "scores": {"faithfulness": 0, "answer_relevance": 0, "context_precision": 0}}

@api.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_path = f"backend/data/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # RAG motoruna yeni dosyayı tanıt
        rag_engine.add_document(file_path)
        
        return {"message": f"{file.filename} başarıyla yüklendi ve indekslendi."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
