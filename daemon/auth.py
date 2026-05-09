import base64
import uuid
import inspect

USERS = {
    "admin": "123",
    "user": "abc"
}

SESSIONS = {}

def check_cookie(headers):
    cookie_header = headers.get("cookie")
    if not cookie_header:
        return None
        
    parts = cookie_header.split(";")
    for p in parts:
        if "=" in p:
            k, v = p.strip().split("=", 1)
            if k == "session" and v in SESSIONS:
                return SESSIONS[v]
    return None

def check_basic_auth(headers):
    auth_header = headers.get("authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return None
    try:
        encoded_credentials = auth_header.split(" ", 1)[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
        if USERS.get(username) == password:
            return username
    except Exception:
        return None
    return None

def require_auth(func):
    async def async_wrapper(*args, **kwargs):
        headers = kwargs.get("headers", {})
        user = check_cookie(headers)
        if not user:
            return (
                b"HTTP/1.1 401 Unauthorized\r\n"
                b"WWW-Authenticate: Basic realm=\"Login Required\"\r\n"
                b"Content-Length: 12\r\n\r\nUnauthorized"
            )
        return await func(*args, **kwargs)

    def sync_wrapper(*args, **kwargs):
        headers = kwargs.get("headers", {})
        user = check_cookie(headers) or check_basic_auth(headers)
        if not user:
            return (
                b"HTTP/1.1 401 Unauthorized\r\n"
                b"WWW-Authenticate: Basic realm=\"Login Required\"\r\n"
                b"Content-Length: 12\r\n\r\nUnauthorized"
            )
        return func(*args, **kwargs)

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

def create_session(username):
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = username
    return session_id