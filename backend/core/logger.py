import logging
import json
import os
from datetime import datetime
from typing import Any, Dict

class EnterpriseLogger:
    def __init__(self, service_name: str = "FinAgent"):
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        # Konsol Handler
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
        # Audit Log (Denetim Kaydı) - JSON formatında dosyaya yazar
        self.audit_path = "backend/data/audit_logs.jsonl"
        os.makedirs(os.path.dirname(self.audit_path), exist_ok=True)

    def info(self, message: str, extra: Dict[str, Any] = None):
        self.logger.info(message, extra=extra)

    def error(self, message: str, error: Exception = None):
        self.logger.error(f"{message} | Error: {str(error)}")

    def audit(self, action: str, user_id: str, details: Dict[str, Any]):
        """
        Finansal denetim için kritik olayları yapılandırılmış formatta kaydeder.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details,
            "version": "1.0.0"
        }
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        self.logger.info(f"AUDIT: {action} for user {user_id}")

logger = EnterpriseLogger()
