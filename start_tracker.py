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
start_tracker
~~~~~~~~~~~~~

This module launches the Tracker application for managing peer registration
in the P2P network. The Tracker server listens for peer registration requests,
maintains a registry of active peers, and serves peer information to requesting clients.

The Tracker is responsible for:
- Registering new peers joining the network
- Maintaining a list of active peers
- Providing peer information to other peers for P2P communication
- Handling peer unregistration
"""

import argparse
from apps import create_tracker

PORT = 7000  # Default Tracker port

if __name__ == "__main__":
    # Parse command-line arguments to configure Tracker server IP and port
    parser = argparse.ArgumentParser(
        prog='Tracker',
        description='P2P Network Tracker - Manages peer registration and discovery',
        epilog='Tracker daemon for AsynapRous P2P framework'
    )
    parser.add_argument('--server-ip', default='0.0.0.0', help='Server IP address to bind to')
    parser.add_argument('--server-port', type=int, default=PORT, help='Server port number')
 
    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port

    # Launch the Tracker application
    create_tracker(ip, port)
