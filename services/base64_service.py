# C:\Users\900803\Downloads\L2ToolsV2\services\base64_service.py
import base64

def decode_base64_to_bytes(b64_string: str) -> bytes:
    if not b64_string or not isinstance(b64_string, str):
        raise ValueError("String base64 kosong atau tidak valid")
    b = b64_string.strip()
    if b.startswith("data:"):
        b = b.split(",", 1)[1]
    b = b.replace("\n", "").replace("\\n", "")
    return base64.b64decode(b)
