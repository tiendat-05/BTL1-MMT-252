#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# AsynapRous release
#

"""
apps.peer
~~~~~~~~~

This module provides a Peer application for P2P network communication.
Each peer can receive messages, broadcast to other peers, and register with a tracker.
"""

import json
import urllib.request
from daemon import AsynapRous

app = AsynapRous()

# In-memory storage for received messages (đã thêm cấu trúc Channel)
channels = {"general": []}  # Dictionary: { "channel_name": [msg1, msg2] }
peer_name = None  # Current peer identifier
tracker_info = None  # Tracker server info


@app.route('/message', methods=['POST'])
def receive_message(headers, body):
    """
    Receive a message from another peer.
    """
    try:
        data = json.loads(body)
        channel = data.get('channel', 'general') # Lấy channel, mặc định là general
        
        # Nếu kênh chưa tồn tại, tạo mới kênh đó
        if channel not in channels:
            channels[channel] = []
            
        channels[channel].append(data)
        
        sender = data.get('from', 'unknown')
        msg = data.get('msg', '')
        print(f"[Peer {peer_name} | Channel: {channel}] <<< RECEIVED from {sender}: {msg}")
        
        # Đếm tổng số tin nhắn trên tất cả các kênh
        total_messages = sum(len(msgs) for msgs in channels.values())
        return json.dumps({"status": "received", "message_count": total_messages}).encode()
    except Exception as e:
        print(f"[Peer {peer_name}] Error receiving message: {e}")
        return json.dumps({"status": "error", "message": str(e)}).encode()


@app.route('/messages', methods=['GET'])
def get_messages(headers, body):
    """
    Retrieve all received messages grouped by channels.
    """
    total_messages = sum(len(msgs) for msgs in channels.values())
    print(f"[Peer {peer_name}] Retrieving {total_messages} messages across {len(channels)} channels")
    return json.dumps({"channels": channels, "total_count": total_messages}).encode()


@app.route('/broadcast', methods=['POST'])
def broadcast(headers, body):
    """
    Broadcast a message to all other registered peers.
    """
    try:
        data = json.loads(body)
        msg_content = data.get("msg", "")
        channel = data.get("channel", "general") # Lấy channel người dùng muốn gửi
        
        print(f"[Peer {peer_name} | Channel: {channel}] >>> BROADCASTING: {msg_content}")
        
        if not tracker_info:
            return json.dumps({
                "status": "error",
                "message": "Not connected to tracker"
            }).encode()
        
        # Get peer list from tracker
        try:
            tracker_url = f"http://{tracker_info['ip']}:{tracker_info['port']}/peers"
            req = urllib.request.Request(tracker_url, method='GET')
            # Thêm timeout để không bị treo
            response = urllib.request.urlopen(req, timeout=3)
            peers_data = json.loads(response.read().decode())
            peers_list = peers_data.get('peers', [])
        except Exception as e:
            print(f"[Peer {peer_name}] Error fetching peers from tracker: {e}")
            return json.dumps({"status": "error", "message": "Failed to get peer list"}).encode()
        
        # Send message to each peer
        sent_count = 0
        failed_count = 0
        
        msg_payload = {
            "from": peer_name,
            "msg": msg_content,
            "channel": channel,
            "time": data.get("time", "")
        }
        
        # Lưu tin nhắn của chính mình vào bộ nhớ của mình
        if channel not in channels:
            channels[channel] = []
        channels[channel].append(msg_payload)
        
        for peer_info in peers_list:
            peer_port = peer_info.get('port')
            peer_ip = peer_info.get('ip')
            
            # Don't send to self
            if peer_port == app.port:
                continue
            
            try:
                url = f"http://{peer_ip}:{peer_port}/message"
                req = urllib.request.Request(
                    url,
                    data=json.dumps(msg_payload).encode(),
                    method='POST',
                    headers={'Content-Type': 'application/json'}
                )
                # Đặt timeout=3 để đảm bảo tính "Non-blocking" giả lập cho urllib
                urllib.request.urlopen(req, timeout=3)
                sent_count += 1
                print(f"[Peer {peer_name}] >>> Sent to {peer_ip}:{peer_port}")
            except Exception as e:
                failed_count += 1
                print(f"[Peer {peer_name}] Failed to send to {peer_ip}:{peer_port}: {e}")
        
        return json.dumps({
            "status": "broadcast_complete",
            "sent": sent_count,
            "failed": failed_count
        }).encode()
    except Exception as e:
        print(f"[Peer {peer_name}] Broadcast error: {e}")
        return json.dumps({"status": "error", "message": str(e)}).encode()


@app.route('/register', methods=['POST'])
def register_with_tracker(headers, body):
    """
    Register this peer with the Tracker server.
    """
    try:
        data = json.loads(body)
        global tracker_info
        
        tracker_info = {
            "ip": data.get("tracker_ip", "127.0.0.1"),
            "port": data.get("tracker_port", 7000)
        }
        
        # FIX HARDCODE IP: Lấy IP thật của app, nếu là 0.0.0.0 thì quy về 127.0.0.1 (chạy local)
        peer_ip = app.ip if app.ip != "0.0.0.0" else "127.0.0.1"
        
        # Send registration to tracker
        reg_payload = {
            "name": peer_name,
            "ip": peer_ip,
            "port": app.port
        }
        
        url = f"http://{tracker_info['ip']}:{tracker_info['port']}/register"
        req = urllib.request.Request(
            url,
            data=json.dumps(reg_payload).encode(),
            method='POST',
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req, timeout=3)
        result = json.loads(response.read().decode())
        
        print(f"[Peer {peer_name}] Registered with tracker at {tracker_info['ip']}:{tracker_info['port']}")
        print(f"[Peer {peer_name}] Tracker returned {len(result.get('peers', []))} peers")
        
        return json.dumps({
            "status": "registered",
            "peer_name": peer_name,
            "tracker": tracker_info
        }).encode()
    except Exception as e:
        print(f"[Peer {peer_name}] Registration error: {e}")
        return json.dumps({"status": "error", "message": str(e)}).encode()


@app.route('/status', methods=['GET'])
def get_status(headers, body):
    """
    Get the current status of this peer.
    """
    total_messages = sum(len(msgs) for msgs in channels.values())
    return json.dumps({
        "peer_name": peer_name,
        "port": app.port,
        "tracker": tracker_info,
        "active_channels": list(channels.keys()),
        "message_count": total_messages
    }).encode()


def create_peer(name, ip="0.0.0.0", port=9002, tracker_ip="127.0.0.1", tracker_port=7000):
    global peer_name, tracker_info
    
    peer_name = name
    tracker_info = {
        "ip": tracker_ip,
        "port": tracker_port
    }
    
    app.prepare_address(ip, port)
    print(f"\n{'=' * 60}")
    print(f"[Peer {peer_name}] Starting on {ip}:{port}")
    print(f"[Peer {peer_name}] Tracker: {tracker_ip}:{tracker_port}")
    print(f"{'=' * 60}\n")
    app.run()