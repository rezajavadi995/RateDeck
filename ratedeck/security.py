from __future__ import annotations
import hashlib, os, re
from pathlib import Path
from cryptography.fernet import Fernet

SECRET_PATTERN=re.compile(r"(?i)(token|secret|api[_-]?key|password)(\s*[=:]\s*)([^\s,;]+)")
def redact(value: str) -> str: return SECRET_PATTERN.sub(lambda m:m.group(1)+m.group(2)+"[REDACTED]",value)

class SecretBox:
    def __init__(self,key: bytes): self.fernet=Fernet(key); self.fingerprint=hashlib.sha256(key).hexdigest()[:12]
    @classmethod
    def load_or_create(cls,path: Path):
        if path.exists(): key=path.read_bytes().strip()
        else:
            path.parent.mkdir(parents=True,exist_ok=True); key=Fernet.generate_key()
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,"wb") as f:f.write(key+b"\n")
        if path.stat().st_mode & 0o077: raise PermissionError("master key permissions must be 0600")
        return cls(key)
    def encrypt(self,value: str)->bytes:return self.fernet.encrypt(value.encode())
    def decrypt(self,value: bytes)->str:return self.fernet.decrypt(value).decode()

