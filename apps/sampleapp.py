import json
import socket
import urllib.request
from daemon import AsynapRous
from daemon.auth import create_session, USERS, require_auth

app = AsynapRous()

# --- Dữ liệu mô phỏng (In-memory) cho P2P ---
peers = {} # {name: {"ip": ip, "port": port}}
messages = [] # Danh sách tin nhắn

# ====================================================
# CÁC ROUTE TỪ TASK 2 (XỬ LÝ AUTH & ASYNC)
# ====================================================
@app.route('/login', methods=['POST'])
def login(headers="guest", body="anonymous"):
    try:
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")
    except:
        return json.dumps({"error": "invalid json"}).encode()

    if USERS.get(username) != password:
        return json.dumps({"error": "unauthorized"}).encode()

    session_id = create_session(username)

    return json.dumps({
        "message": "login success",
        "session": session_id
    }).encode()

@app.route('/echo', methods=['POST'])
@require_auth
def echo(headers="guest", body="anonymous"):
    try:
        data = json.loads(body)
        return json.dumps({"received": data}).encode()
    except:
        return json.dumps({"error": "invalid json"}).encode()

@app.route('/hello', methods=['PUT'])
@require_auth
async def hello(headers, body):
    print("[App] async hello")
    return json.dumps({"msg": "hello async"}).encode()

# ====================================================
# CÁC ROUTE CŨ CHO P2P (TRACKER VÀ PEER)
# ====================================================
@app.route('/register', methods=['POST'])
def register(headers, body):
    data = json.loads(body)
    name = data.get("name")
    peers[name] = {"ip": data.get("ip"), "port": data.get("port")}
    print(f"[Tracker] Registered peer: {name}")
    return json.dumps({"status": "success", "peers": list(peers.values())}).encode()

@app.route('/peers', methods=['GET'])
def get_peers(headers, body):
    return json.dumps({"peers": list(peers.values())}).encode()

@app.route('/message', methods=['POST'])
def receive_message(headers, body):
    data = json.loads(body)
    messages.append(data)
    print(f"[Peer] New message from {data['from']}: {data['msg']}")
    return json.dumps({"status": "received"}).encode()

@app.route('/broadcast', methods=['POST'])
def broadcast(headers, body):
    data = json.loads(body)
    msg_payload = {
        "from": data.get("name"),
        "msg": data.get("msg"),
        "time": data.get("time")
    }
    
    # Gửi tới tất cả peers (P2P logic)
    for name, info in peers.items():
        if info['port'] != data.get("my_port"):
            url = f"http://{info['ip']}:{info['port']}/message"
            try:
                req = urllib.request.Request(
                    url, data=json.dumps(msg_payload).encode(), 
                    method='POST', headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req)
            except Exception as e:
                print(f"Failed to send to {name}: {e}")
                
    # Add to local messages list
    messages.append(msg_payload)

    return json.dumps({"status": "broadcast_complete"}).encode()

@app.route('/messages', methods=['GET'])
def get_messages(headers, body):
    return json.dumps({"messages": messages}).encode()

@app.route('/chat', methods=['GET'])
def serve_chat(headers, body):
    try:
        with open("www/chat.html", "r", encoding="utf-8") as f:
            html = f.read()
        return html.encode()
    except:
        return b"<h1>chat.html not found</h1>"


def create_sampleapp(ip="0.0.0.0", port=2026):
    """
    Create and launch the sample application with Tracker, Peer, Auth and Async functionality.
    """
    app.prepare_address(ip, port)
    print(f"[SampleApp] Starting Full App on {ip}:{port}")
    app.run()