from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Mesaj geçmişini tutar, add_messages ile yeni mesajlar eklenir
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # Kullanıcı bilgileri (örn. account_id)
    user_info: dict
    # Mevcut işlem durumu (örn. "risk_approved", "pending_transfer")
    next_step: str
    # Kritik işlemler için onay bayrağı
    is_risk_cleared: bool
