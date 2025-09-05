import hmac, os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("INTERNAL_API_SECRET", "")
if not SECRET:
    raise RuntimeError("INTERNAL_API_SECRET not set")

def verify_internal_secret(x_internal_secret: str = Header(default="")):
    if not hmac.compare_digest(x_internal_secret, SECRET):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
