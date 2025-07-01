#!/usr/bin/env python3
# ghostwire - Complete P2P Communication Tool

import socket
import threading
import argparse
import json
import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

BLOCK_SIZE = 16
DATA_FILE = "/tmp/ghostwire_data.json"
CONFIG_FILE = "/tmp/ghostwire_config.json"

class GhostwireServer:
    def __init__(self, port, key, alias):
        self.port = port
        self.key = key
        self.alias = alias
        self.clients = {}  # socket -> user info
        self.users = {}    # username -> info
        self.running = False
        self.load_data()
    
    def load_data(self):
        """Load existing user data"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
            except:
                pass
    
    def save_data(self):
        """Save user data"""
        try:
            data = {'users': self.users}
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
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
        # Wait for client to send username first
        try:
            data = client_socket.recv(1024)
            if not data:
                client_socket.close()
                return
            
            username_data = data.decode('utf-8')
            if username_data.startswith('USERNAME:'):
                username = username_data.split(':', 1)[1].strip()
                
                # Handle special commands
                if username == "LIST_CMD":
                    self.send_user_list(client_socket)
                    client_socket.close()
                    return
                    
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
                    # Broadcast to other clients
                    self.broadcast_to_all(f"[{username}]: {decrypted_message}", exclude_socket=client_socket)
        
        except Exception as e:
            print(f"[ERROR] Client {username} error: {e}")
        finally:
            self.remove_client(client_socket)
    
    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(10)
        self.running = True
        
        print(f"[SERVER] Ghostwire '{self.alias}' started on port {self.port}")
        print(f"[SERVER] Waiting for connections...")
        
        try:
            while self.running:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        
        except KeyboardInterrupt:
            print("\\n[SERVER] Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        for client_socket in list(self.clients.keys()):
            self.remove_client(client_socket)
        
        try:
            self.server_socket.close()
        except:
            pass
        
        self.save_data()
        print("[SERVER] Server stopped")
    
    def create_user(self, username):
        """Create a new user"""
        self.users[username] = {'created': True}
        self.save_data()
        print(f"[INFO] User '{username}' created")
    
    def send_user_list(self, client_socket):
        """Send user list to requesting client"""
        connected_users = [user_info['username'] for user_info in self.clients.values()]
        created_users = list(self.users.keys())
        
        user_list = f"Connected: {', '.join(connected_users)} | Created: {', '.join(created_users)}"
        encrypted_response = self.encrypt_message(user_list)
        
        try:
            client_socket.send(encrypted_response.encode('utf-8'))
        except:
            pass
    
    def list_users(self):
        """List all users"""
        print("\\n[USERS] Connected users:")
        for client_socket, user_info in self.clients.items():
            print(f"  - {user_info['username']} ({user_info['address'][0]})")
        
        print("\\n[USERS] Created users:")
        for username in self.users:
            print(f"  - {username}")
        print()

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
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
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
    
    def send_message(self, message):
        """Send a single message"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            encrypted_message = self.encrypt_message(message)
            self.socket.send(encrypted_message.encode('utf-8'))
            
            print(f"[INFO] Message sent: {message}")
            
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
        finally:
            if self.socket:
                self.socket.close()
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            self.socket.close()

def save_config(port, key):
    """Save connection config for easy access"""
    config = {
        'port': port,
        'key': base64.b64encode(key).decode('utf-8')
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    """Load saved connection config"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config['port'], base64.b64decode(config['key'].encode('utf-8'))
        except:
            pass
    return None, None

def main():
    parser = argparse.ArgumentParser(description='Ghostwire - Encrypted P2P Communication Tool')
    parser.add_argument('--port', type=int, help='Port number (default: 2222)', default=2222)
    parser.add_argument('--key1', help='First encryption key')
    parser.add_argument('--key2', help='Second encryption key')
    parser.add_argument('--key3', help='Third encryption key')
    parser.add_argument('--enable', action='store_true', help='Enable server')
    parser.add_argument('--alias', help='Server alias (required for --enable)')
    parser.add_argument('--create-user', help='Create a new user')
    parser.add_argument('--send', help='Send a message')
    parser.add_argument('--all', action='store_true', help='Send to all users')
    parser.add_argument('--to', help='Send to specific user')
    parser.add_argument('--disable', action='store_true', help='Disable server')
    parser.add_argument('--list-all', action='store_true', help='List all users')
    parser.add_argument('--user', help='Your username for sending messages')
    parser.add_argument('--daemon', action='store_true', help='Run client in daemon mode (no interactive chat)')
    
    args = parser.parse_args()
    
    # Try to load existing config first
    saved_port, saved_key = load_config()
    
    # Generate encryption key from the three keys if provided
    if args.key1 and args.key2 and args.key3:
        key = pad((args.key1 + args.key2 + args.key3).encode(), BLOCK_SIZE)
        save_config(args.port, key)
    elif saved_key:
        key = saved_key
        args.port = saved_port if not args.port else args.port
    else:
        if args.send:
            print("[ERROR] No saved connection. Please run server first or provide keys.")
            return
        key = b'0' * 16  # dummy key
    
    if args.enable:
        # Start server with room name (alias)
        if not args.alias:
            print("[ERROR] --alias (room name) required when starting server")
            return
        
        server = GhostwireServer(args.port, key, args.alias)
        
        if args.create_user:
            server.create_user(args.create_user)
            print(f"[INFO] Created user '{args.create_user}' in room '{args.alias}'")
        
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
    
    elif args.send:
        # Send message using saved username or provided username
        username = args.create_user if args.create_user else args.user if args.user else "anonymous"
        
        try:
            client = GhostwireClient('localhost', args.port, key, username)
            client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.socket.connect(('localhost', args.port))
            
            # Send username first
            client.socket.send(f"USERNAME:{username}".encode('utf-8'))
            
            if args.all:
                print(f"[INFO] Sending to all users: {args.send}")
                encrypted_message = client.encrypt_message(args.send)
                client.socket.send(encrypted_message.encode('utf-8'))
                print(f"[INFO] Message sent: [{username}]: {args.send}")
            elif args.to:
                print(f"[INFO] Sending private message to {args.to}: {args.send}")
                encrypted_message = client.encrypt_message(f"@{args.to} {args.send}")
                client.socket.send(encrypted_message.encode('utf-8'))
                print(f"[INFO] Private message sent to {args.to}")
            else:
                print("[ERROR] Please specify --all or --to username")
                
            client.socket.close()
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
    
    elif args.list_all:
        # List users by connecting temporarily
        try:
            client = GhostwireClient('localhost', args.port, key, "temp_list_user")
            client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.socket.connect(('localhost', args.port))
            
            # Send special command to list users
            client.socket.send("USERNAME:LIST_USERS_CMD".encode('utf-8'))
            
            # Wait for response
            response = client.socket.recv(1024).decode('utf-8')
            if response:
                decrypted = client.decrypt_message(response)
                if decrypted:
                    print(f"[INFO] {decrypted}")
                else:
                    print("[INFO] Connected users list requested")
            
            client.socket.close()
        except Exception as e:
            print(f"[ERROR] Failed to list users: {e}")
        
    elif args.disable:
        print(f"[INFO] Room '{args.alias}' on port {args.port} disabled")
        # Send shutdown signal to server
        
    else:
        # Connect as client to room
        if not args.create_user:
            print("[ERROR] --create-user (username) required when joining room")
            return
        
        if not args.alias:
            print("[ERROR] --alias (room name) required when joining room")
            return
            
        print(f"[INFO] Joining room '{args.alias}' as user '{args.create_user}'")
        client = GhostwireClient('localhost', args.port, key, args.create_user)
        client.connect()

if __name__ == "__main__":
    main()

