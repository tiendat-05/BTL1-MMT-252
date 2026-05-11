#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# AsynapRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
apps.tracker
~~~~~~~~~~~~~

This module provides a Tracker application that manages peer registration
and serves peer information to connected clients.
"""

import json
from daemon import AsynapRous

app = AsynapRous()

# In-memory storage for registered peers
peers = {}  # {name: {"ip": ip, "port": port}}


@app.route('/register', methods=['POST'])
def register(headers, body):
    """
    Register a new peer with the Tracker.
    
    Expects JSON body with:
    - name: peer identifier
    - ip: peer IP address
    - port: peer port number
    
    Returns list of all registered peers.
    """
    data = json.loads(body)
    name = data.get("name")
    peers[name] = {"name": name, "ip": data.get("ip"), "port": data.get("port")}
    print(f"[Tracker] Registered peer: {name} at {data.get('ip')}:{data.get('port')}")
    return json.dumps({"status": "success", "peers": list(peers.values())}).encode()


@app.route('/peers', methods=['GET'])
def get_peers(headers, body):
    """
    Retrieve the list of all registered peers.
    
    Returns JSON with peer list.
    """
    print(f"[Tracker] Peer list requested. Total peers: {len(peers)}")
    return json.dumps({"peers": list(peers.values())}).encode()


@app.route('/unregister', methods=['POST'])
def unregister(headers, body):
    """
    Unregister a peer from the Tracker.
    
    Expects JSON body with:
    - name: peer identifier to remove
    """
    data = json.loads(body)
    name = data.get("name")
    if name in peers:
        del peers[name]
        print(f"[Tracker] Unregistered peer: {name}")
        return json.dumps({"status": "success", "message": f"Peer {name} unregistered"}).encode()
    else:
        return json.dumps({"status": "error", "message": f"Peer {name} not found"}).encode()


def create_tracker(ip="0.0.0.0", port=7000):
    """
    Create and launch the Tracker application.
    
    The Tracker manages peer registration and serves peer information.
    
    :param ip (str): IP address to bind the server (default: '0.0.0.0')
    :param port (int): Port number to listen on (default: 7000)
    """
    app.prepare_address(ip, port)
    print(f"[Tracker] Starting Tracker on {ip}:{port}")
    print("[Tracker] Ready to accept peer registrations...")
    app.run()
