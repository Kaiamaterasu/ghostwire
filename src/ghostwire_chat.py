#!/usr/bin/env python3
# ghostwire_chat.py - Working P2P chat implementation

import socket
import threading
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import sys

BLOCK_SIZE = 16
clients = []  # Store all connected clients
client_aliases = {}  # Map socket to alias

def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), BLOCK_SIZE))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv + " " + ct

def decrypt_message(encrypted_message, key):
    try:
        iv, ct = encrypted_message.split(" ", 1)
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
        return pt.decode('utf-8')
    except:
        return None

def broadcast_to_all(message, key, exclude_socket=None):
    """Send message to all connected clients"""
    encrypted_msg = encrypt_message(message, key)
    dead_clients = []
    
    for client_socket in clients:
        if client_socket != exclude_socket:
            try:
                client_socket.send(encrypted_msg.encode('utf-8'))
            except:
                dead_clients.append(client_socket)
    
    # Remove dead clients
    for dead_client in dead_clients:
        if dead_client in clients:
            clients.remove(dead_client)
        if dead_client in client_aliases:
            del client_aliases[dead_client]

def handle_client(client_socket, address, key):
    """Handle individual client connection"""
    alias = f"user_{address[1]}"  # Use port as temp alias
    client_aliases[client_socket] = alias
    
    print(f"[INFO] {alias} connected from {address}")
    broadcast_to_all(f"[SYSTEM] {alias} joined the room", key, exclude_socket=client_socket)
    
    try:
        while True:
            # Receive message from client
            data = client_socket.recv(1024)
            if not data:
                break
                
            encrypted_message = data.decode('utf-8')
            decrypted_message = decrypt_message(encrypted_message, key)
            
            if decrypted_message:
                print(f"[{alias}]: {decrypted_message}")
                # Broadcast to all other clients
                broadcast_to_all(f"[{alias}]: {decrypted_message}", key, exclude_socket=client_socket)
            
    except Exception as e:
        print(f"[ERROR] Client {alias} error: {e}")
    finally:
        # Clean up
        if client_socket in clients:
            clients.remove(client_socket)
        if client_socket in client_aliases:
            del client_aliases[client_socket]
        client_socket.close()
        print(f"[INFO] {alias} disconnected")
        broadcast_to_all(f"[SYSTEM] {alias} left the room", key)

def start_chat_server(port, key):
    """Start the chat server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    
    print(f"[SERVER] Ghostwire Chat Server started on port {port}")
    print(f"[SERVER] Waiting for connections...")
    
    try:
        while True:
            client_socket, address = server_socket.accept()
            clients.append(client_socket)
            
            # Handle client in separate thread
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, address, key)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\\n[SERVER] Shutting down...")
    finally:
        server_socket.close()

def start_chat_client(host, port, key, alias):
    """Start chat client"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
        print(f"[CLIENT] Connected to Ghostwire server at {host}:{port}")
        print(f"[CLIENT] Your alias: {alias}")
        print("Type messages and press Enter. Type 'quit' to exit.\\n")
        
        # Start receiving thread
        def receive_messages():
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    encrypted_message = data.decode('utf-8')
                    decrypted_message = decrypt_message(encrypted_message, key)
                    
                    if decrypted_message:
                        print(f"\\r{decrypted_message}")
                        print(f"{alias}: ", end="", flush=True)
                        
                except:
                    break
        
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Main chat loop
        while True:
            message = input(f"{alias}: ")
            
            if message.lower() == 'quit':
                break
                
            if message.strip():
                encrypted_message = encrypt_message(message, key)
                client_socket.send(encrypted_message.encode('utf-8'))
                
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
    finally:
        client_socket.close()

def server_console(key):
    """Server console for sending messages"""
    print("Server console ready. Type messages to broadcast to all clients.")
    print("Type 'quit' to stop server.\\n")
    
    while True:
        try:
            message = input("[SERVER]: ")
            if message.lower() == 'quit':
                break
            if message.strip():
                broadcast_to_all(f"[SERVER]: {message}", key)
        except KeyboardInterrupt:
            break

def main():
    """Main function for chat system"""
    # Generate key from Ghostwire keys
    encoded_key = pad(("57575" + "6464" + "7766").encode(), BLOCK_SIZE)
    
    mode = input("Start as (s)erver or (c)lient? ").lower()
    
    if mode == 's':
        # Start server with console
        server_thread = threading.Thread(target=start_chat_server, args=(5050, encoded_key))
        server_thread.daemon = True
        server_thread.start()
        
        time.sleep(1)  # Let server start
        server_console(encoded_key)
        
    elif mode == 'c':
        alias = input("Enter your alias: ")
        start_chat_client('localhost', 5050, encoded_key, alias)
        
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()

