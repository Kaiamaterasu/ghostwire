#!/usr/bin/env python3
# ghostwire_broadcast.py - Enhanced server that broadcasts to all clients

import socket
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

BLOCK_SIZE = 16
clients = []  # List to store all connected clients

def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), BLOCK_SIZE))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv + " " + ct

def decrypt_message(encrypted_message, key):
    iv, ct = encrypted_message.split()
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
    return pt.decode('utf-8')

def broadcast_message(message, sender_socket, key):
    """Broadcast message to all connected clients except sender"""
    encrypted_msg = encrypt_message(message, key)
    for client in clients:
        if client != sender_socket:
            try:
                client.send(encrypted_msg.encode('utf-8'))
            except:
                clients.remove(client)

def handle_client(client_socket, key):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            decrypted_msg = decrypt_message(message, key)
            print(f"Received: {decrypted_msg}")
            
            # Broadcast to other clients
            broadcast_message(f"[CLIENT]: {decrypted_msg}", client_socket, key)
            
        except Exception as e:
            print(f"Error handling client: {e}")
            break
    
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()

def start_broadcast_server(port, key):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen()
    print(f"Broadcast server started on port {port}")
    
    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address}")
        clients.append(client_socket)
        
        client_thread = threading.Thread(target=handle_client, args=(client_socket, key))
        client_thread.start()

def send_server_message(message, key):
    """Send a message from server to all clients"""
    encrypted_msg = encrypt_message(f"[SERVER]: {message}", key)
    for client in clients:
        try:
            client.send(encrypted_msg.encode('utf-8'))
        except:
            clients.remove(client)

def main():
    """Main function for broadcast server"""
    # Use same keys as main Ghostwire
    encoded_key = pad(("57575" + "6464" + "7766").encode(), BLOCK_SIZE)
    
    # Start server in a thread
    server_thread = threading.Thread(target=start_broadcast_server, args=(5051, encoded_key))
    server_thread.daemon = True
    server_thread.start()
    
    # Interactive server console
    try:
        while True:
            msg = input("Server message: ")
            if msg.lower() == 'quit':
                break
            send_server_message(msg, encoded_key)
    except KeyboardInterrupt:
        print("Server shutting down...")

if __name__ == "__main__":
    main()

