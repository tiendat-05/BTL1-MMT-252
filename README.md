p2p:

b1:

mở 3 terminal
- terminal 1: python start_tracker.py //(port 7000)
- terminal 2: python start_peer1.py //(port 9002)
- terminal 3: python start_peer2.py //(port 9003)

b2:

postman:

peer1:

method: POST

URL: http://127.0.0.1:9002/register

Body (JSON):

{
  "tracker_ip": "127.0.0.1",
  "tracker_port": 7000
}

peer2:

Method: POST

URL: http://127.0.0.1:9003/register

Body (JSON): Dùng y hệt cục JSON ở trên.

b3:

Gửi request bắt Peer 1 Broadcast tin nhắn:

Method: POST

URL: http://127.0.0.1:9002/broadcast

Body (JSON):
{
  "msg": "Xin chao, toi la Peer 1!",
  "time": "2026-04-19"
}

Terminal Peer 1 sẽ in ra log báo đang gửi tin nhắn đi (BROADCASTING...).

Terminal Peer 2 sẽ in ra log báo nhận được tin nhắn từ Peer 1 (RECEIVED...).

ở broadcast:

{
  "msg": "Ai đó rảnh làm bài tập Mạng máy tính không?",
  "channel": "hoc_tap",
  "time": "2026-04-19"
}

GET http://127.0.0.1:9002/messages, bạn sẽ thấy các tin nhắn được chia ra thành từng khối riêng biệt theo tên kênh

Asynchronous Python HTTP Server:

b1: chạy python start_sampleapp.py

copy ip (0.0.0.0:2026)

b2: postman

method: POST

URL: 0.0.0.0:2026/login

xem trong file auth.py có tên admin, user 

nhập API

JSON:
{
    "username": "admin",
    "password": "123"
}

send

kết quả:

{
    "message": "login success"
}

b3: chạy method: PUT, URL: 0.0.0.0:2026/hello, JSON như trên

kết quả:

{
    "msg": "hello async"
}

proxy

b1:

chạy 4 terminal

python start_backend.py --server-port 9001

python start_backend.py --server-port 9002

python start_backend.py --server-port 9003

python start_proxy.py

b2: postman

method: GET

URL: http://localhost:8080

ở headers:

thêm key: Host, value: app.local

send

-> kết quả thu về ở terminal 4, bấm send liên tục thực hiện như round robin
