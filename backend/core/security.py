import re
import time
from typing import Dict, List

class SecurityProvider:
    def __init__(self):
        self.rate_limit_storage: Dict[str, List[float]] = {}
        self.suspicious_patterns = [
            r"(sql|drop|delete|select|update|insert)\s", # Basic SQLi check
            r"<script>", # Basic XSS check
            r"\.\./" # Path traversal
        ]

    def mask_pii(self, text: str) -> str:
        """
        TC Kimlik, Kredi Kartı, Telefon ve E-posta gibi hassas verileri maskeler.
        """
        # TC Kimlik (11 hane)
        text = re.sub(r'\b[1-9][0-9]{10}\b', '********TR', text)
        
        # Kredi Kartı (16 hane)
        text = re.sub(r'\b[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}\b', '****-****-****-****', text)
        
        # Telefon
        text = re.sub(r'\b(05|5)[0-9]{9}\b', '05*********', text)

        # E-posta
        text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', '*****@*****.com', text)
        
        return text

    def check_threats(self, text: str) -> bool:
        """
        Girdi içerisinde şüpheli örüntüler arar.
        """
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def is_rate_limited(self, user_id: str, limit: int = 10, window: int = 60) -> bool:
        """
        Basit bir in-memory rate limiter. (Dakikada 10 istek)
        """
        now = time.time()
        if user_id not in self.rate_limit_storage:
            self.rate_limit_storage[user_id] = []
        
        # Pencere dışındaki istekleri temizle
        self.rate_limit_storage[user_id] = [t for t in self.rate_limit_storage[user_id] if now - t < window]
        
        if len(self.rate_limit_storage[user_id]) >= limit:
            return True
        
        self.rate_limit_storage[user_id].append(now)
        return False

security_audit = SecurityProvider()
