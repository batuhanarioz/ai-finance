from fastmcp import FastMCP
import random

# FastMCP sunucusunu başlatıyoruz
mcp = FastMCP("ArchitechtBanking")

# Mock Veri Seti
MOCK_ACCOUNTS = {
    "TR001": {"name": "Batuhan Arıöz", "balance": 150000.0, "currency": "TRY"},
    "TR002": {"name": "Architecht HR", "balance": 500000.0, "currency": "TRY"},
}

@mcp.tool()
def get_market_rates(currency: str = "USD") -> str:
    """Canlı döviz ve altın kurlarını getirir."""
    rates = {"USD": "32.45 TRY", "EUR": "35.10 TRY", "XAU": "2.450 TRY (Gram Altın)"}
    return f"{currency} için güncel kur: {rates.get(currency.upper(), 'Veri bulunamadı')}"

@mcp.tool()
def get_balance(account_id: str) -> str:
    """Hesap bakiyesini sorgular."""
    account = MOCK_ACCOUNTS.get(account_id)
    if account:
        return f"{account['name']} isimli kullanıcının bakiyesi: {account['balance']} {account['currency']}"
    return "Hesap bulunamadı."

@mcp.tool()
def execute_transfer(sender_id: str, receiver_id: str, amount: float) -> str:
    """Para transferi işlemini gerçekleştirir."""
    if sender_id not in MOCK_ACCOUNTS:
        return "Gönderici hesap bulunamadı."
    
    if MOCK_ACCOUNTS[sender_id]["balance"] < amount:
        return "Yetersiz bakiye."
    
    # İşlem simülasyonu
    MOCK_ACCOUNTS[sender_id]["balance"] -= amount
    if receiver_id in MOCK_ACCOUNTS:
        MOCK_ACCOUNTS[receiver_id]["balance"] += amount
        
    return f"{amount} TRY başarıyla {receiver_id} hesabına gönderildi. Yeni bakiye: {MOCK_ACCOUNTS[sender_id]['balance']} TRY"

@mcp.tool()
def get_credit_score(customer_id: str) -> int:
    """Müşterinin kredi skorunu döndürür (1-1900 arası)."""
    # Simülasyon: TR001 için yüksek, diğerleri için rastgele
    if customer_id == "TR001":
        return 1850
    return random.randint(300, 1500)

@mcp.tool()
def verify_account(account_id: str) -> dict:
    """Hesap numarasının geçerli olup olmadığını ve kime ait olduğunu kontrol eder."""
    account = MOCK_ACCOUNTS.get(account_id)
    if account:
        return {"status": "valid", "owner": account["name"], "currency": account["currency"]}
    return {"status": "invalid", "owner": None}

@mcp.tool()
def deposit_money(account_id: str, amount: float) -> str:
    """Belirtilen hesaba para yüklemesi yapar."""
    if account_id not in MOCK_ACCOUNTS:
        return "Hesap bulunamadı."
    
    MOCK_ACCOUNTS[account_id]["balance"] += amount
    return f"{amount} TRY başarıyla hesaba yüklendi. Yeni bakiye: {MOCK_ACCOUNTS[account_id]['balance']} TRY"

if __name__ == "__main__":
    mcp.run()
