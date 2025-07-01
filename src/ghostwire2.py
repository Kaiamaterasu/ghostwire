#!/usr/bin/env python3
# ghostwire2 - Fixed P2P Communication Tool

import socket
import threading
import argparse
import json
import sys
import os
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

BLOCK_SIZE = 16
DATA_FILE = "/tmp/ghostwire_data.json"
CONFIG_FILE = "/tmp/ghostwire_config.json"
DAEMON_SOCKET = "/tmp/ghostwire_daemon.sock"

class GhostwireDaemon:
    def __init__(self, port, key, alias):
        self.port = port
        self.key = key
        self.alias = alias
        self.clients = {}
        self.users = {}
        self.running = False
        self.daemon_socket = None
        
    def encrypt_message(self, message):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message.encode(), BLOCK_SIZE))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv + " " + ct
    
    def decrypt_message(self, encrypted_message):
        try:
            iv, ct = encrypted_message.split(" ", 1)
            iv = base64.b64decode(iv)
            ct = base64.b64decode(ct)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
            return pt.decode('utf-8')
        except:
            return None
    
    def broadcast_to_all(self, message, exclude_socket=None):
        """Send message to all connected clients"""
        encrypted_msg = self.encrypt_message(message)
        dead_clients = []
        
        for client_socket in self.clients:
            if client_socket != exclude_socket:
                try:
                    client_socket.send(encrypted_msg.encode('utf-8'))
                except:
                    dead_clients.append(client_socket)
        
        for dead_client in dead_clients:
            self.remove_client(dead_client)
    
    def send_to_user(self, message, target_user):
        """Send message to specific user"""
        encrypted_msg = self.encrypt_message(message)
        
        for client_socket, user_info in self.clients.items():
            if user_info['username'] == target_user:
                try:
                    client_socket.send(encrypted_msg.encode('utf-8'))
                    return True
                except:
                    self.remove_client(client_socket)
        return False
    
    def remove_client(self, client_socket):
        """Remove client connection"""
        if client_socket in self.clients:
            user_info = self.clients[client_socket]
            username = user_info.get('username', 'Unknown')
            print(f"[INFO] {username} disconnected")
            del self.clients[client_socket]
            self.broadcast_to_all(f"[SYSTEM] {username} left the room")
        
        try:
            client_socket.close()
        except:
            pass
    
    def handle_client(self, client_socket, address):
        """Handle individual client"""
        try:
            data = client_socket.recv(1024)
            if not data:
                client_socket.close()
                return
            
            username_data = data.decode('utf-8')
            if username_data.startswith('USERNAME:'):
                username = username_data.split(':', 1)[1].strip()
            else:
                username = f"user_{address[1]}"
            
            self.clients[client_socket] = {'username': username, 'address': address}
            
            print(f"[INFO] {username} connected from {address}")
            self.broadcast_to_all(f"[SYSTEM] {username} joined the room", exclude_socket=client_socket)
        except:
            client_socket.close()
            return
        
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                encrypted_message = data.decode('utf-8')
                decrypted_message = self.decrypt_message(encrypted_message)
                
                if decrypted_message:
                    print(f"[{username}]: {decrypted_message}")
                    self.broadcast_to_all(f"[{username}]: {decrypted_message}", exclude_socket=client_socket)
        
        except Exception as e:
            print(f"[ERROR] Client {username} error: {e}")
        finally:
            self.remove_client(client_socket)
    
    def handle_daemon_command(self, conn):
        """Handle commands from daemon interface"""
        try:
            data = conn.recv(1024).decode('utf-8')
            command = json.loads(data)
            
            if command['action'] == 'send_all':
                message = f"[{command['username']}]: {command['message']}"
                self.broadcast_to_all(message)
                print(message)
                conn.send(b"OK")
                
            elif command['action'] == 'send_to':
                message = f"[PRIVATE from {command['username']} to {command['target']}]: {command['message']}"
                success = self.send_to_user(message, command['target'])
                print(message)
                conn.send(b"OK" if success else b"FAILED")
                
            elif command['action'] == 'list_users':
                connected = [info['username'] for info in self.clients.values()]
                response = json.dumps({"connected": connected, "created": list(self.users.keys())})
                conn.send(response.encode('utf-8'))
                
        except Exception as e:
            print(f"[ERROR] Daemon command error: {e}")
            conn.send(b"ERROR")
        finally:
            conn.close()
    
    def start_daemon_interface(self):
        """Start Unix socket for command interface"""
        try:
            os.unlink(DAEMON_SOCKET)
        except:
            pass
            
        self.daemon_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.daemon_socket.bind(DAEMON_SOCKET)
        self.daemon_socket.listen(10)
        
        while self.running:
            try:
                conn, addr = self.daemon_socket.accept()
                threading.Thread(target=self.handle_daemon_command, args=(conn,), daemon=True).start()
            except:
                break
    
    def start(self):
        """Start the daemon"""
        # Start main server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(10)
        self.running = True
        
        # Save config for command interface
        config = {
            'port': self.port,
            'key': base64.b64encode(self.key).decode('utf-8'),
            'alias': self.alias
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        
        print(f"[SERVER] Ghostwire '{self.alias}' started on port {self.port}")
        print(f"[SERVER] Waiting for connections...")
        
        # Start daemon interface
        daemon_thread = threading.Thread(target=self.start_daemon_interface, daemon=True)
        daemon_thread.start()
        
        try:
            while self.running:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
        
        except KeyboardInterrupt:
            print("\\n[SERVER] Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the daemon"""
        self.running = False
        
        for client_socket in list(self.clients.keys()):
            self.remove_client(client_socket)
        
        try:
            self.server_socket.close()
        except:
            pass
            
        try:
            self.daemon_socket.close()
            os.unlink(DAEMON_SOCKET)
        except:
            pass
        
        print("[SERVER] Server stopped")

def send_daemon_command(command):
    """Send command to running daemon"""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(DAEMON_SOCKET)
        sock.send(json.dumps(command).encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        sock.close()
        return response
    except Exception as e:
        print(f"[ERROR] Failed to send command to daemon: {e}")
        return None

class GhostwireClient:
    def __init__(self, host, port, key, alias):
        self.host = host
        self.port = port
        self.key = key
        self.alias = alias
        self.socket = None
        self.running = False
    
    def encrypt_message(self, message):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message.encode(), BLOCK_SIZE))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv + " " + ct
    
    def decrypt_message(self, encrypted_message):
        try:
            iv, ct = encrypted_message.split(" ", 1)
            iv = base64.b64decode(iv)
            ct = base64.b64decode(ct)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
            return pt.decode('utf-8')
        except:
            return None
    
    def receive_messages(self):
        """Receive messages from server"""
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                encrypted_message = data.decode('utf-8')
                decrypted_message = self.decrypt_message(encrypted_message)
                
                if decrypted_message:
                    print(f"\\r{decrypted_message}")
                    print(f"{self.alias}: ", end="", flush=True)
            
            except:
                break
    
    def connect(self):
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            # Send username to server
            self.socket.send(f"USERNAME:{self.alias}".encode('utf-8'))
            
            print(f"[CLIENT] Connected to Ghostwire server at {self.host}:{self.port}")
            print(f"[CLIENT] Your username: {self.alias}")
            print("Type messages and press Enter. Type 'quit' to exit.\\n")
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
            # Main chat loop
            while self.running:
                message = input(f"{self.alias}: ")
                
                if message.lower() == 'quit':
                    break
                
                if message.strip():
                    encrypted_message = self.encrypt_message(message)
                    self.socket.send(encrypted_message.encode('utf-8'))
        
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        finally:
            self.disconnect()
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            self.socket.close()

def main():
    parser = argparse.ArgumentParser(description='Ghostwire2 - Fixed P2P Communication Tool')
    parser.add_argument('--port', type=int, help='Port number (default: 2222)', default=2222)
    parser.add_argument('--key1', help='First encryption key')
    parser.add_argument('--key2', help='Second encryption key')
    parser.add_argument('--key3', help='Third encryption key')
    parser.add_argument('--enable', action='store_true', help='Enable server')
    parser.add_argument('--alias', help='Server/room name')
    parser.add_argument('--create-user', help='Username when joining')
    parser.add_argument('--send', help='Send a message')
    parser.add_argument('--all', action='store_true', help='Send to all users')
    parser.add_argument('--to', help='Send to specific user')
    parser.add_argument('--list-all', action='store_true', help='List all users')
    
    args = parser.parse_args()
    
    if args.enable:
        # Start server daemon
        if not all([args.key1, args.key2, args.key3, args.alias]):
            print("[ERROR] --key1, --key2, --key3, and --alias required for server")
            return
        
        key = pad((args.key1 + args.key2 + args.key3).encode(), BLOCK_SIZE)
        daemon = GhostwireDaemon(args.port, key, args.alias)
        
        if args.create_user:
            daemon.users[args.create_user] = {'created': True}
            print(f"[INFO] Created user '{args.create_user}'")
        
        daemon.start()
    
    elif args.send:
        # Send command to daemon
        if not args.create_user:
            print("[ERROR] --create-user required for sending messages")
            return
        
        if args.all:
            command = {
                'action': 'send_all',
                'username': args.create_user,
                'message': args.send
            }
            response = send_daemon_command(command)
            if response == "OK":
                print(f"[INFO] Message sent to all: [{args.create_user}]: {args.send}")
            else:
                print("[ERROR] Failed to send message")
        
        elif args.to:
            command = {
                'action': 'send_to',
                'username': args.create_user,
                'target': args.to,
                'message': args.send
            }
            response = send_daemon_command(command)
            if response == "OK":
                print(f"[INFO] Private message sent to {args.to}")
            else:
                print("[ERROR] Failed to send private message")
        else:
            print("[ERROR] Use --all or --to <username>")
    
    elif args.list_all:
        # List users via daemon
        command = {'action': 'list_users'}
        response = send_daemon_command(command)
        if response:
            try:
                data = json.loads(response)
                print(f"[USERS] Connected: {', '.join(data['connected'])}")
                print(f"[USERS] Created: {', '.join(data['created'])}")
            except:
                print("[ERROR] Failed to parse user list")
    
    else:
        # Show help for command-line usage
        print("[INFO] Ghostwire2 - Command Line Usage:")
        print("")
        print("To start a server:")
        print("  --enable --key1 <k1> --key2 <k2> --key3 <k3> --alias <room-name>")
        print("")
        print("To send messages:")
        print("  --send 'message' --create-user <username> --all")
        print("  --send 'message' --create-user <username> --to <target-user>")
        print("")
        print("To list users:")
        print("  --list-all")
        print("")
        print("No interactive mode - pure command line only!")

if __name__ == "__main__":
    main()

