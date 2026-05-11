# AsynapRous - Asynchronous Python HTTP Framework

## Mục lục
- [1. P2P Chat System](#1-p2p-chat-system)
- [2. Asynchronous HTTP Server (Authentication)](#2-asynchronous-http-server-authentication)
- [3. Reverse Proxy (Load Balancer)](#3-reverse-proxy-load-balancer)

---

## 1. P2P Chat System

### Bước 1: Khởi chạy hệ thống (3 Terminal)

```bash
# Terminal 1: Tracker Server (port 7000)
python start_tracker.py

# Terminal 2: Peer 1 (port 9002)
python start_peer1.py

# Terminal 3: Peer 2 (port 9003)
python start_peer2.py
```

### Bước 2: Đăng ký Peer với Tracker (Postman)

**Peer 1 đăng ký:**

| Thuộc tính | Giá trị |
|---|---|
| Method | `POST` |
| URL | `http://127.0.0.1:9002/register` |

Body (JSON):
```json
{
  "tracker_ip": "127.0.0.1",
  "tracker_port": 7000
}
```

**Peer 2 đăng ký:** Dùng y hệt JSON ở trên, chỉ đổi URL:

| Thuộc tính | Giá trị |
|---|---|
| Method | `POST` |
| URL | `http://127.0.0.1:9003/register` |

### Bước 3: Broadcast tin nhắn (Channel: general)

| Thuộc tính | Giá trị |
|---|---|
| Method | `POST` |
| URL | `http://127.0.0.1:9002/broadcast` |

Body (JSON):
```json
{
  "msg": "Xin chao, toi la Peer 1!",
  "time": "2026-04-19"
}
```

**Kết quả:**
- Terminal Peer 1 → in log `BROADCASTING...` (đang gửi)
- Terminal Peer 2 → in log `RECEIVED...` (đã nhận từ Peer 1)

### Bước 4: Broadcast theo Channel (kênh riêng)

| Thuộc tính | Giá trị |
|---|---|
| Method | `POST` |
| URL | `http://127.0.0.1:9002/broadcast` |

Body (JSON):
```json
{
  "msg": "Ai đó rảnh làm bài tập Mạng máy tính không?",
  "channel": "hoc_tap",
  "time": "2026-04-19"
}
```

### Bước 5: Xem tin nhắn theo Channel

| Thuộc tính | Giá trị |
|---|---|
| Method | `GET` |
| URL | `http://127.0.0.1:9002/messages` |

**Kết quả:** Tin nhắn được chia thành từng khối riêng biệt theo tên kênh (`general`, `hoc_tap`,...).

### Bước 6: Chat trên giao diện Web (Browser)

Sau khi đã đăng ký ở Bước 2, mở trình duyệt:

- Peer 1: `http://127.0.0.1:9002/chat`
- Peer 2: `http://127.0.0.1:9003/chat`

**Tính năng giao diện:**
- **Tab "General (All)"**: Broadcast tin nhắn tới tất cả peer
- **Click vào tên peer**: Mở tab DM (Direct Message) — chat riêng P2P 1-1
- **Online Peers**: Hiển thị danh sách peer đang online, tự động cập nhật
- **Tắt Tracker**: 2 peer vẫn chat được (dùng cached peer list) — chứng minh P2P thật

### Bước 7: Demo P2P thuần (tắt Tracker)

1. Tắt Tracker (Ctrl+C ở Terminal 1)
2. Ở trình duyệt, 2 peer vẫn chat qua lại bình thường
3. Log peer hiện: `"Tracker offline, using cached peer list"`

---

## 2. Asynchronous HTTP Server (Authentication)

### Bước 1: Khởi chạy SampleApp

```bash
python start_sampleapp.py
```

Server chạy trên `0.0.0.0:2026`.

### Bước 2: Đăng nhập (Login)

| Thuộc tính | Giá trị |
|---|---|
| Method | `POST` |
| URL | `http://0.0.0.0:2026/login` |

Tài khoản có sẵn trong `daemon/auth.py`: `admin/123`, `user/abc`

Body (JSON):
```json
{
  "username": "admin",
  "password": "123"
}
```

**Kết quả:**
```json
{
  "message": "login success"
}
```

Response Header sẽ có `Set-Cookie: session=<uuid>` — đây là Session-based Authentication (RFC 6265).

### Bước 3: Gọi API được bảo vệ

| Thuộc tính | Giá trị |
|---|---|
| Method | `PUT` |
| URL | `http://0.0.0.0:2026/hello` |

Body (JSON):
```json
{
  "username": "admin",
  "password": "123"
}
```

**Kết quả:**
```json
{
  "msg": "hello async"
}
```

> **Lưu ý:** Nếu không gửi kèm Cookie hoặc Basic Auth header, server sẽ trả về `401 Unauthorized`.

---

## 3. Reverse Proxy (Load Balancer)

### Bước 1: Khởi chạy (4 Terminal)

```bash
# Terminal 1: Backend server 1
python start_backend.py --server-port 9001

# Terminal 2: Backend server 2
python start_backend.py --server-port 9002

# Terminal 3: Backend server 3
python start_backend.py --server-port 9003

# Terminal 4: Proxy server (port 8080)
python start_proxy.py
```

### Bước 2: Gửi request qua Proxy (Postman)

| Thuộc tính | Giá trị |
|---|---|
| Method | `GET` |
| URL | `http://localhost:8080` |

**Headers:**

| Key | Value |
|---|---|
| Host | `app.local` |

### Kết quả

Bấm **Send** liên tục, quan sát Terminal 4 (Proxy) — request sẽ được phân phối luân phiên (Round Robin) tới 3 backend server:

```
Request 1 → Backend 9001
Request 2 → Backend 9002
Request 3 → Backend 9003
Request 4 → Backend 9001  (quay lại)
...
```

---

## Chuyển đổi chế độ Non-blocking

Mở file `daemon/backend.py`, sửa dòng `mode_async`:

```python
# Chế độ 1: Multi-threading
mode_async = "threading"

# Chế độ 2: Coroutine (asyncio)
mode_async = "coroutine"
```

---

## Xử lý lỗi thường gặp

### Port bị chiếm (OSError: [Errno 10048])
```powershell
# Tìm process đang chiếm port
netstat -ano | Select-String "LISTENING" | Select-String ":7000"

# Kill bằng PID
Stop-Process -Id <PID> -Force
```

### Tắt tất cả server đang chạy
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```
