#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# AsynapRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
start_peer1
~~~~~~~~~~~

This module launches Peer 1 instance for P2P network communication.
Peer 1 listens on port 9002 by default and connects to the Tracker server.
"""

import argparse
from apps import create_peer

PEER_NAME = "peer1"
PEER_PORT = 9002  # Default port for Peer 1
TRACKER_PORT = 7000  # Default tracker port

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        prog='Peer1',
        description='P2P Peer 1 - Communicates via Tracker',
        epilog='Peer daemon for AsynapRous P2P framework'
    )
    parser.add_argument('--peer-ip', default='0.0.0.0', help='Peer server IP address to bind to')
    parser.add_argument('--peer-port', type=int, default=PEER_PORT, help='Peer server port number')
    parser.add_argument('--tracker-ip', default='127.0.0.1', help='Tracker server IP address')
    parser.add_argument('--tracker-port', type=int, default=TRACKER_PORT, help='Tracker server port')
 
    args = parser.parse_args()
    
    # Launch Peer 1
    create_peer(
        name=PEER_NAME,
        ip=args.peer_ip,
        port=args.peer_port,
        tracker_ip=args.tracker_ip,
        tracker_port=args.tracker_port
    )
