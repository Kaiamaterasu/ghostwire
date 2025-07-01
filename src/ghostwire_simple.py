#!/usr/bin/env python3
# ghostwire_simple.py - Clean Command-Line Only P2P Communication Tool

import socket
import threading
import argparse
import json
import sys
import os
import time
import signal
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

BLOCK_SIZE = 16
DATA_FILE = "/tmp/ghostwire_data.json"
CONFIG_FILE = "/tmp/ghostwire_config.json"

class GhostwireServer:
    def __init__(self, port, key, alias, creator_username):
        self.port = port
        self.key = key
        self.alias = alias
        self.creator = creator_username  # Store the creator username
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
            data = {'users': self.users, 'creator': self.creator}
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
        username = None
        try:
            # Wait for client to send username first
            data = client_socket.recv(1024)
            if not data:
                client_socket.close()
                return
            
            username_data = data.decode('utf-8')
            if username_data.startswith('USERNAME:'):
                username = username_data.split(':', 1)[1].strip()
                
                # Handle special commands
                if username == "LIST_USERS_CMD":
                    self.send_user_list(client_socket)
                    client_socket.close()
                    return
                    
            else:
                client_socket.close()
                return
            
            # Ensure user exists in users list
            if username not in self.users:
                self.users[username] = {'created': True}
            
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
                    # Check if it's a private message
                    if decrypted_message.startswith('@'):
                        # Private message format: @username message
                        parts = decrypted_message.split(' ', 1)
                        if len(parts) >= 2:
                            target_user = parts[0][1:]  # Remove @
                            private_msg = parts[1]
                            success = self.send_to_user(f"[PRIVATE from {username}]: {private_msg}", target_user)
                            if success:
                                # COMPLETE PRIVACY - NO LOGGING AT ALL
                                # Send confirmation to sender
                                confirmation = self.encrypt_message(f"[SYSTEM] Private message sent to {target_user}")
                                client_socket.send(confirmation.encode('utf-8'))
                            else:
                                # Send error to sender
                                error_msg = self.encrypt_message(f"[SYSTEM] User {target_user} not found")
                                client_socket.send(error_msg.encode('utf-8'))
                    else:
                        # Public message - show in server log
                        print(f"[{username}]: {decrypted_message}")
                        # Broadcast to other clients
                        self.broadcast_to_all(f"[{username}]: {decrypted_message}", exclude_socket=client_socket)
        
        except Exception as e:
            print(f"[ERROR] Client {username} error: {e}")
        finally:
            self.remove_client(client_socket)
    
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
    
    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(10)
        self.running = True
        
        print(f"[SERVER] Ghostwire '{self.alias}' started on port {self.port}")
        print(f"[SERVER] Room created by: {self.creator}")
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
            print("\n[SERVER] Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Send termination message to all connected users before disconnecting them
        termination_message = f"[SYSTEM]: The room port {self.port} has been terminated"
        print(f"[SERVER] Broadcasting termination message to {len(self.clients)} users")
        
        # Send termination message to all clients
        for client_socket in list(self.clients.keys()):
            try:
                encrypted_msg = self.encrypt_message(termination_message)
                client_socket.send(encrypted_msg.encode('utf-8'))
                # Give a moment for message to be sent
                time.sleep(0.1)
            except:
                pass
        
        # Now disconnect all clients
        for client_socket in list(self.clients.keys()):
            self.remove_client(client_socket)
        
        try:
            self.server_socket.close()
        except:
            pass
        
        self.save_data()
        print(f"[SERVER] Server on port {self.port} stopped")

def send_message(host, port, key, username, message, target_user=None, users={}):
    """Send a message to the server"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # Send username first
        client_socket.send(f"USERNAME:{username}".encode('utf-8'))
        
        # Prepare message
        if target_user:
            full_message = f"@{target_user} {message}"
        else:
            full_message = message
        
        # Encrypt and send message
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(full_message.encode(), BLOCK_SIZE))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        encrypted_message = iv + " " + ct
        
        client_socket.send(encrypted_message.encode('utf-8'))
        
        # Wait for confirmation if private message
        if target_user:
            try:
                response = client_socket.recv(1024).decode('utf-8')
                if response:
                    iv, ct = response.split(" ", 1)
                    iv = base64.b64decode(iv)
                    ct = base64.b64decode(ct)
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
                    confirmation = pt.decode('utf-8')
                    print(f"[INFO] {confirmation}")
            except:
                pass
        
        if target_user:
            print(f"[INFO] Private message sent to {target_user}: {message}")
        else:
            print(f"[INFO] Message sent to all: {message}")
        
        client_socket.close()
        
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

def join_room_persistent(host, port, key, username):
    """Join room and stay connected to receive and send messages"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # Send username to join
        client_socket.send(f"USERNAME:{username}".encode('utf-8'))
        
        print(f"[INFO] Connected to room as {username}")
        print(f"[INFO] You are now in the room. Type messages to send. Ctrl+C to leave.")
        print("-" * 50)
        
        # Start thread to listen for incoming messages
        def listen_for_messages():
            try:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    try:
                        encrypted_message = data.decode('utf-8')
                        iv, ct = encrypted_message.split(" ", 1)
                        iv = base64.b64decode(iv)
                        ct = base64.b64decode(ct)
                        cipher = AES.new(key, AES.MODE_CBC, iv)
                        pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
                        message = pt.decode('utf-8')
                        print(message)
                    except Exception as e:
                        print(f"[ERROR] Failed to decrypt message: {e}")
            except:
                pass
        
        # Start listening thread
        import threading
        listen_thread = threading.Thread(target=listen_for_messages)
        listen_thread.daemon = True
        listen_thread.start()
        
        # Handle user input for sending messages
        try:
            while True:
                try:
                    user_input = input(f"[{username}]: ")
                    if user_input.strip():
                        # Check if it's a private message (starts with @)
                        if user_input.startswith('@'):
                            full_message = user_input
                        else:
                            full_message = user_input
                        
                        # Encrypt and send message
                        cipher = AES.new(key, AES.MODE_CBC)
                        ct_bytes = cipher.encrypt(pad(full_message.encode(), BLOCK_SIZE))
                        iv = base64.b64encode(cipher.iv).decode('utf-8')
                        ct = base64.b64encode(ct_bytes).decode('utf-8')
                        encrypted_message = iv + " " + ct
                        
                        client_socket.send(encrypted_message.encode('utf-8'))
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        
        except KeyboardInterrupt:
            print(f"\n[INFO] {username} leaving room...")
        
        client_socket.close()
        
    except Exception as e:
        print(f"[ERROR] Failed to join room: {e}")

def create_user_in_room(host, port, key, username):
    """Create user ID in room and STAY CONNECTED to receive messages"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # Send username to create user
        client_socket.send(f"USERNAME:{username}".encode('utf-8'))
        
        print(f"[INFO] User '{username}' created and joined the room")
        print(f"[INFO] You are now connected and will see all messages")
        print(f"[INFO] Use another terminal to send messages with --send")
        print(f"[INFO] Press Ctrl+C to leave the room")
        print("-" * 50)
        
        # Save the username and room info for future use
        user_config = {
            'username': username, 
            'port': port,
            'host': host,
            'key': base64.b64encode(key).decode('utf-8')
        }
        try:
            with open('/tmp/ghostwire_user.json', 'w') as f:
                json.dump(user_config, f)
        except:
            pass
        
        # Start thread to listen for incoming messages
        def listen_for_messages():
            try:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    try:
                        encrypted_message = data.decode('utf-8')
                        iv, ct = encrypted_message.split(" ", 1)
                        iv = base64.b64decode(iv)
                        ct = base64.b64decode(ct)
                        cipher = AES.new(key, AES.MODE_CBC, iv)
                        pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
                        message = pt.decode('utf-8')
                        print(message)
                    except Exception as e:
                        print(f"[ERROR] Failed to decrypt message: {e}")
            except:
                pass
        
        # Start listening thread
        listen_thread = threading.Thread(target=listen_for_messages)
        listen_thread.daemon = True
        listen_thread.start()
        
        # Handle user input for sending messages
        try:
            while True:
                try:
                    user_input = input(f"[{username}]: ")
                    if user_input.strip():
                        # Check for steganography commands
                        if user_input.startswith('/stealth '):
                            handle_stealth_command(user_input, username)
                            continue
                        elif user_input.startswith('/extract '):
                            handle_extract_command(user_input, username)
                            continue
                        elif user_input == '/help':
                            print("Commands:")
                            print("  @username message     - Send private message")
                            print("  /stealth image.jpg \"message\" output.png key @user - Hide message in image")
                            print("  /extract image.png key - Extract message from image")
                            print("  /help - Show this help")
                            continue
                        
                        # Check if it's a private message (starts with @)
                        if user_input.startswith('@'):
                            full_message = user_input
                        else:
                            full_message = user_input
                        
                        # Encrypt and send message
                        cipher = AES.new(key, AES.MODE_CBC)
                        ct_bytes = cipher.encrypt(pad(full_message.encode(), BLOCK_SIZE))
                        iv = base64.b64encode(cipher.iv).decode('utf-8')
                        ct = base64.b64encode(ct_bytes).decode('utf-8')
                        encrypted_message = iv + " " + ct
                        
                        client_socket.send(encrypted_message.encode('utf-8'))
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        
        except KeyboardInterrupt:
            print(f"\n[INFO] {username} leaving room...")
        
        client_socket.close()
        
    except Exception as e:
        print(f"[ERROR] Failed to create user: {e}")

def get_saved_user_config():
    """Get the saved user config from previous --create-user"""
    try:
        with open('/tmp/ghostwire_user.json', 'r') as f:
            user_config = json.load(f)
            return user_config
    except:
        return None

def get_saved_username():
    """Get the saved username from previous --create-user"""
    config = get_saved_user_config()
    return config.get('username') if config else None

def handle_stealth_command(user_input, username):
    """Handle /stealth command in interactive mode"""
    try:
        # Parse: /stealth image.jpg "message" output.png key @user
        parts = user_input.split()
        if len(parts) < 5:
            print("Usage: /stealth image.jpg \"message\" output.png key [@user|@all]")
            return
        
        image_path = parts[1]
        # Handle quoted message
        if '"' in user_input:
            start_quote = user_input.find('"')
            end_quote = user_input.find('"', start_quote + 1)
            if start_quote != -1 and end_quote != -1:
                message = user_input[start_quote+1:end_quote]
                remaining = user_input[end_quote+1:].strip().split()
                if len(remaining) >= 2:
                    output_path = remaining[0]
                    stego_key = remaining[1]
                    target = remaining[2] if len(remaining) > 2 else "@all"
                else:
                    print("Usage: /stealth image.jpg \"message\" output.png key [@user|@all]")
                    return
            else:
                print("Message must be in quotes")
                return
        else:
            print("Message must be in quotes")
            return
        
        if not os.path.exists(image_path):
            print(f"Error: Image file {image_path} not found")
            return
        
        # Hide message in image
        from ghostwire_steganography import GhostwireSteganography
        stego = GhostwireSteganography(stego_key, None, None)
        success, result = stego.hide_message_in_image(image_path, message, output_path)
        
        if success:
            print(f"✅ {result}")
            print(f"🔒 Message encrypted with key: {stego_key}")
            print(f"📁 Steganographic image saved to: {output_path}")
            
            if target.startswith('@'):
                if target == "@all":
                    print(f"📤 Send {output_path} to all users")
                else:
                    target_user = target[1:]
                    print(f"📤 Send {output_path} to {target_user}")
        else:
            print(f"❌ {result}")
    
    except Exception as e:
        print(f"Error in stealth command: {e}")

def handle_extract_command(user_input, username):
    """Handle /extract command in interactive mode"""
    try:
        # Parse: /extract image.png key
        parts = user_input.split()
        if len(parts) < 3:
            print("Usage: /extract image.png key")
            return
        
        image_path = parts[1]
        stego_key = parts[2]
        
        if not os.path.exists(image_path):
            print(f"Error: Image file {image_path} not found")
            return
        
        # Extract message from image
        from ghostwire_steganography import GhostwireSteganography
        stego = GhostwireSteganography(stego_key, None, None)
        success, result = stego.extract_message_from_image(image_path)
        
        if success:
            print("✅ Message extracted successfully:")
            print("📝 Hidden message:")
            print("-" * 30)
            print(result)
            print("-" * 30)
            print(f"🔓 Message decrypted with key: {stego_key}")
        else:
            print(f"❌ {result}")
    
    except Exception as e:
        print(f"Error in extract command: {e}")

def list_users(host, port, key):
    """List all users"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # Send special command to list users
        client_socket.send("USERNAME:LIST_USERS_CMD".encode('utf-8'))
        
        # Wait for response
        response = client_socket.recv(1024).decode('utf-8')
        if response:
            try:
                iv, ct = response.split(" ", 1)
                iv = base64.b64decode(iv)
                ct = base64.b64decode(ct)
                cipher = AES.new(key, AES.MODE_CBC, iv)
                pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
                user_list = pt.decode('utf-8')
                print(f"[USERS] {user_list}")
            except:
                print("[ERROR] Failed to decrypt user list")
        else:
            print("[INFO] No users found")
        
        client_socket.close()
        
    except Exception as e:
        print(f"[ERROR] Failed to list users: {e}")

def save_config(port, key, alias, creator):
    """Save connection config for easy access"""
    config = {
        'port': port,
        'key': base64.b64encode(key).decode('utf-8'),
        'alias': alias,
        'creator': creator
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    """Load saved connection config"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return (config['port'], 
                       base64.b64decode(config['key'].encode('utf-8')), 
                       config.get('alias', 'default'),
                       config.get('creator', 'unknown'))
        except:
            pass
    return None, None, None, None

def main():
    parser = argparse.ArgumentParser(description='Ghostwire - Command-Line Only P2P Communication Tool')
    parser.add_argument('--port', type=int, help='Port number (default: 2222)', default=2222)
    parser.add_argument('--host', help='Host to connect to (default: localhost)', default='localhost')
    parser.add_argument('--key1', help='First encryption key')
    parser.add_argument('--key2', help='Second encryption key')
    parser.add_argument('--key3', help='Third encryption key')
    parser.add_argument('--enable', action='store_true', help='Enable server')
    parser.add_argument('--alias', help='Server alias/room name')
    parser.add_argument('--create-user', help='Your username (only needed when starting server)')
    parser.add_argument('--user', help='Your username for sending messages')
    parser.add_argument('--send', help='Send a message')
    parser.add_argument('--all', action='store_true', help='Send to all users')
    parser.add_argument('--to', help='Send to specific user')
    parser.add_argument('--list-all', action='store_true', help='List all users')
    
    # Steganography options (simplified)
    parser.add_argument('--stealthimage', help='Hide message in image')
    parser.add_argument('--extract', help='Extract message from steganographic image')
    parser.add_argument('--message', help='Secret message to hide')
    parser.add_argument('--out', help='Output image name')
    parser.add_argument('--key', help='Steganography key for encryption')

    args = parser.parse_args()
    
    # Handle steganography commands first
    if args.stealthimage or args.extract:
        from ghostwire_steganography import GhostwireSteganography
        
        # Use steganography key or fallback to main keys
        stego_key = args.key if args.key else None
        if not stego_key and args.key1 and args.key2 and args.key3:
            stego_key = args.key1 + args.key2 + args.key3
        
        if args.stealthimage:
            # Hide message in image
            if not args.message:
                print("Error: --message is required when hiding message in image")
                return
            
            if not args.out:
                print("Error: --out is required when hiding message in image")
                return
            
            if not os.path.exists(args.stealthimage):
                print(f"Error: Image file {args.stealthimage} not found")
                return
            
            # Initialize steganography with single key
            stego = GhostwireSteganography(stego_key, None, None)
            success, result = stego.hide_message_in_image(
                args.stealthimage, args.message, args.out
            )
            
            if success:
                print(f"✅ {result}")
                if stego_key:
                    print("🔒 Message encrypted with steganography key")
                print(f"📁 Steganographic image saved to: {args.out}")
            else:
                print(f"❌ {result}")
                return
        
        elif args.extract:
            # Extract message from image
            if not os.path.exists(args.extract):
                print(f"Error: Image file {args.extract} not found")
                return
            
            # Initialize steganography with single key
            stego = GhostwireSteganography(stego_key, None, None)
            success, result = stego.extract_message_from_image(args.extract)
            
            if success:
                print("✅ Message extracted successfully:")
                print("📝 Hidden message:")
                print("-" * 50)
                print(result)
                print("-" * 50)
                if stego_key:
                    print("🔓 Message decrypted with steganography key")
            else:
                print(f"❌ {result}")
                return
        
        return  # Exit after handling steganography commands
    
    saved_port, saved_key, saved_alias, saved_creator = load_config()
    
    # Generate encryption key from the three keys if provided
    if args.key1 and args.key2 and args.key3:
        key = pad((args.key1 + args.key2 + args.key3).encode(), BLOCK_SIZE)
        alias = args.alias or 'default'
        creator = args.create_user or 'server-admin'
        save_config(args.port, key, alias, creator)
    elif saved_key:
        key = saved_key
        if not args.port or args.port == 2222:
            args.port = saved_port
        if not args.alias:
            args.alias = saved_alias
    else:
        if args.enable:
            print("[ERROR] --key1, --key2, --key3 required to start server")
            return
        elif args.send or args.list_all:
            print("[ERROR] No saved connection. Please start server first or provide keys.")
            return
        else:
            print("[ERROR] --key1, --key2, --key3 required")
            return
    
    if args.enable:
        if not args.alias:
            print("[ERROR] --alias (room name) required when starting server")
            return
        
        creator = args.create_user or "server-admin"
        server = GhostwireServer(args.port, key, args.alias, creator)
        
        # Set up signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\n[SERVER] Received shutdown signal...")
            server.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
    
    elif args.create_user:
        # Create user in room (quick connect and disconnect)
        username = args.create_user
        create_user_in_room(args.host, args.port, key, username)
    
    elif args.send:
        # Use saved user config from --create-user
        saved_config = get_saved_user_config()
        
        if saved_config:
            # Use saved room info automatically
            username = saved_config['username']
            host = saved_config['host']
            port = saved_config['port']
            key = base64.b64decode(saved_config['key'].encode('utf-8'))
            
            if args.all:
                send_message(host, port, key, username, args.send)
            elif args.to:
                send_message(host, port, key, username, args.send, args.to)
            else:
                print("[ERROR] Please specify --all or --to username")
        else:
            # Fallback to manual specification
            username = args.user or "anonymous"
            if args.all:
                send_message(args.host, args.port, key, username, args.send)
            elif args.to:
                send_message(args.host, args.port, key, username, args.send, args.to)
            else:
                print("[ERROR] Please specify --all or --to username")
    
    elif args.list_all:
        list_users(args.host, args.port, key)
    
    else:
        # Show usage
        print("Ghostwire - Command Line Usage:")
        print("")
        print("To start a server:")
        print("  ghostwire --enable --key1 <k1> --key2 <k2> --key3 <k3> --alias <room-name> --create-user <your-username>")
        print("")
        print("To send messages:")
        print("  ghostwire --send 'message' --user <username> --all")
        print("  ghostwire --send 'message' --user <username> --to <target-user>")
        print("")
        print("To list users:")
        print("  ghostwire --list-all")
        print("")
        print("NOTE: --user is optional for sending messages (defaults to 'anonymous')")

if __name__ == "__main__":
    main()

