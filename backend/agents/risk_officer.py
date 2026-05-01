from pydantic import BaseModel, Field
from typing import Optional
from langchain_openai import ChatOpenAI
from backend.core.state import AgentState

class RiskAnalysis(BaseModel):
    is_safe: bool = Field(description="İşlemin güvenli olup olmadığı")
    risk_score: int = Field(description="0-100 arası risk puanı")
    reason: str = Field(description="Risk kararının gerekçesi")

class RiskOfficer:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o").with_structured_output(RiskAnalysis)

    def analyze_transaction(self, state: AgentState):
        """
        Para transferi veya kredi işlemlerini denetler.
        """
        last_message = state["messages"][-1].content
        user_info = state.get("user_info", {})
        
        # LLM'e kural setini veriyoruz (Guardrail)
        prompt = f"""
        Sen bir Banka Risk Denetim Uzmanısın. 
        Müşteri: {user_info.get('name')} (Kredi Skoru: {user_info.get('credit_score')})
        Talep: {last_message}
        
        KARAR REHBERİ:
        1. Bakiye sorma, hesap özeti isteme veya banka ürünleri hakkında bilgi alma işlemleri TAMAMEN GÜVENLİDİR (is_safe: true).
        2. Sadece PARA TRANSFERİ ve KREDİ (FİNANSMAN) taleplerinde kuralları uygula.
        3. Tek seferde 50.000 TL üzeri transferleri reddet.
        4. Kredi skoru 1500 altı olanların kredi taleplerini reddet.
        """
        
        analysis = self.llm.invoke(prompt)
        return analysis

risk_officer = RiskOfficer()
