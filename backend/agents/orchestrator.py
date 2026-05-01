from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from backend.core.state import AgentState
from backend.core.rag_manager import rag_engine
from backend.agents.risk_officer import risk_officer
from langgraph.checkpoint.memory import MemorySaver
from backend.mcp_server.bank_server import get_balance, execute_transfer, get_credit_score, get_market_rates, verify_account, deposit_money
from backend.core.config import settings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os

llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0)
tools = [get_balance, execute_transfer, get_credit_score, get_market_rates, verify_account, deposit_money]
llm_with_tools = llm.bind_tools(tools)

from backend.core.logger import logger

# --- Node Fonksiyonları ---

def supervisor_node(state: AgentState):
    """Kullanıcı isteğini analiz eder ve ilgili ajana yönlendirir."""
    last_msg = state["messages"][-1].content.lower()
    user_ctx = f"Aktif Kullanıcı: {state['user_info']['name']} (ID: {state['user_info']['account_id']})"
    
    logger.info(f"Supervisor analyzing: {last_msg}", extra={"user_id": state['user_info']['account_id']})
    
    prompt = f"""Sen bir banka orkestratörüsün. {user_ctx}.
    Kullanıcı isteğini analiz et ve bir sonraki adımı belirle:
    1. Eğer işlem (para transferi, ödeme, yükleme) ise -> 'risk_agent'
    2. Eğer bilgi sorgulama (bakiye, hesap bilgisi, kredi skoru) ise -> 'transactional_agent'
    3. Eğer genel bilgi/ürün sorusu ise -> 'product_agent'
    
    İstek: {last_msg}
    Sadece adım ismini dön (risk_agent, transactional_agent, product_agent)."""
    
    response = llm.invoke([SystemMessage(content="Sen bir yönlendiricisin."), HumanMessage(content=prompt)])
    next_step = response.content.strip().lower()
    
    # Güvenlik: Eğer LLM yanlış bir şey dönerse default olarak product'a git
    valid_steps = ["risk_agent", "transactional_agent", "product_agent"]
    if next_step not in valid_steps:
        next_step = "product_agent"
        
    return {"next_step": next_step}

def product_agent_node(state: AgentState):
    """RAG kullanarak bilgi toplar."""
    user_query = state["messages"][-1].content
    context = rag_engine.query(user_query)
    
    prompt = f"Banka dökümanları: {context}\n\nKullanıcı sorusu: {user_query}\n\nLütfen detaylı ve katılım bankacılığı terminolojisine uygun cevap ver."
    response = llm.invoke([SystemMessage(content="Sen uzman bir banka danışmanısın."), HumanMessage(content=prompt)])
    
    # Kendi kendine düzeltme için verileri sakla
    return {"messages": [response], "next_step": "verifier"}

def verifier_node(state: AgentState):
    """Ajanın cevabını denetler (Self-Correction)."""
    last_response = state["messages"][-1].content
    # Burada LLM'e "Bu cevap dökümanlara uygun mu?" diye soruyoruz
    verification_prompt = f"Aşağıdaki cevabı banka kurallarına göre denetle. Hata varsa düzeltilmiş halini yaz, yoksa 'ONAYLANDI' de:\n\n{last_response}"
    v_response = llm.invoke([SystemMessage(content="Sen bir kalite denetim uzmanısın."), HumanMessage(content=verification_prompt)])
    
    if "ONAYLANDI" in v_response.content:
        return {"next_step": END}
    else:
        # Hata bulunduysa düzeltilmiş cevabı ekle
        return {"messages": [v_response], "next_step": END}

def risk_agent_node(state: AgentState):
    """İşlem riskini denetler."""
    analysis = risk_officer.analyze_transaction(state)
    logger.audit("RISK_ANALYSIS", state["user_info"]["account_id"], analysis.dict())
    
    if not analysis.is_safe:
        return {"messages": [AIMessage(content=f"⚠️ GÜVENLİK ENGELİ: {analysis.reason}")], "next_step": END}
    
    # EĞER risk skoru orta seviyedeyse (örn: > 50), onay iste
    if analysis.risk_score > 50:
        logger.info("High risk detected, routing to approval node")
        return {"next_step": "human_approval"}
    
    return {"is_risk_cleared": True, "next_step": "transactional_agent"}

def human_approval_node(state: AgentState):
    """
    Kritik işlemler için insan onayını simüle eder veya bekler.
    Gerçek dünyada burada durup (interrupt) dışarıdan onay bekleriz.
    """
    # Basitlik için burada bir mesaj dönüyoruz, UI tarafında 'onayla' butonu tetiklenebilir.
    msg = "Bu işlem yüksek riskli görünüyor. Devam etmek istediğinizden emin misiniz? (Evet/Hayır)"
    return {"messages": [AIMessage(content=msg)], "next_step": END}

from langgraph.prebuilt import ToolNode

# --- Node Fonksiyonları ---

# ... (supervisor, product, verifier, risk, human_approval aynı kalıyor) ...

def transactional_agent_node(state: AgentState):
    """Banka fonksiyonlarını seçer."""
    user_ctx = f"Aktif Kullanıcı: {state['user_info']['name']} (ID: {state['user_info']['account_id']})"
    system_msg = SystemMessage(content=f"Sen bir bankacısın. {user_ctx}. Kullanıcının kimliği doğrulanmıştır. İşlemleri bu kullanıcı adına gerçekleştir.")
    response = llm_with_tools.invoke([system_msg] + state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Tool çağrısı var mı kontrol eder."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# --- Graph Yapılandırması ---

workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("product_agent", product_agent_node)
workflow.add_node("verifier", verifier_node)
workflow.add_node("transactional_agent", transactional_agent_node)
workflow.add_node("tools", ToolNode(tools)) # Standart ToolNode
workflow.add_node("risk_agent", risk_agent_node)
workflow.add_node("human_approval", human_approval_node)

workflow.set_entry_point("supervisor")

def router(state: AgentState):
    return state["next_step"]

workflow.add_conditional_edges("supervisor", router)
workflow.add_conditional_edges("product_agent", router)
workflow.add_conditional_edges("risk_agent", router)

# Banker için tool döngüsü
workflow.add_conditional_edges("transactional_agent", should_continue)
workflow.add_edge("tools", "transactional_agent") # Tool çalıştıktan sonra tekrar Banker'a dön (cevap yazması için)

workflow.add_edge("verifier", END)
workflow.add_edge("human_approval", END)

app = workflow.compile(checkpointer=MemorySaver())
