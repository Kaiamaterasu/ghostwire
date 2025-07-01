#!/usr/bin/env python3
"""
Ghostwire Steganography Module
Implements LSB (Least Significant Bit) steganography for hiding messages in images
"""

import argparse
import os
import sys
from PIL import Image
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class GhostwireSteganography:
    def __init__(self, key1=None, key2=None, key3=None):
        """Initialize with optional encryption keys"""
        self.encryption_key = None
        if key1 and key2 and key3:
            # Combine three keys for encryption
            combined_key = f"{key1}{key2}{key3}"
            self.encryption_key = combined_key[:32].ljust(32, '0')[:32].encode()
    
    def string_to_binary(self, message):
        """Convert string to binary representation"""
        return ''.join(format(ord(char), '08b') for char in message)
    
    def binary_to_string(self, binary):
        """Convert binary representation back to string"""
        message = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                message += chr(int(byte, 2))
        return message
    
    def encrypt_message(self, message):
        """Encrypt message using AES if keys are provided"""
        if not self.encryption_key:
            return message
        
        try:
            cipher = AES.new(self.encryption_key, AES.MODE_CBC)
            padded_message = pad(message.encode(), AES.block_size)
            encrypted = cipher.encrypt(padded_message)
            
            # Combine IV and encrypted data
            result = base64.b64encode(cipher.iv + encrypted).decode('utf-8')
            return f"ENCRYPTED:{result}"
        except Exception as e:
            print(f"Encryption failed: {e}")
            return message
    
    def decrypt_message(self, encrypted_message):
        """Decrypt message using AES if keys are provided"""
        if not self.encryption_key or not encrypted_message.startswith("ENCRYPTED:"):
            return encrypted_message
        
        try:
            encrypted_data = encrypted_message[10:]  # Remove "ENCRYPTED:" prefix
            data = base64.b64decode(encrypted_data)
            
            iv = data[:16]  # First 16 bytes are IV
            encrypted = data[16:]  # Rest is encrypted message
            
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Decryption failed: {e}")
            return encrypted_message
    
    def hide_message_in_image(self, image_path, message, output_path, encrypt=True):
        """Hide message in image using LSB steganography"""
        try:
            # Load image
            img = Image.open(image_path)
            img = img.convert('RGB')  # Ensure RGB mode
            
            # Encrypt message if keys are provided and encryption is enabled
            if encrypt and self.encryption_key:
                message = self.encrypt_message(message)
            
            # Add delimiter to mark end of message
            message += "<<<GHOSTWIRE_END>>>"
            
            # Convert message to binary
            binary_message = self.string_to_binary(message)
            
            # Get image dimensions
            width, height = img.size
            total_pixels = width * height
            
            # Check if image is large enough
            if len(binary_message) > total_pixels * 3:  # 3 channels (RGB)
                raise ValueError("Image too small to hide the message")
            
            # Convert image to list of pixels
            pixels = list(img.getdata())
            
            # Hide message in LSB of each color channel
            binary_index = 0
            modified_pixels = []
            
            for pixel in pixels:
                if binary_index < len(binary_message):
                    # Get RGB values
                    r, g, b = pixel
                    
                    # Modify LSB of red channel
                    if binary_index < len(binary_message):
                        r = (r & 0xFE) | int(binary_message[binary_index])
                        binary_index += 1
                    
                    # Modify LSB of green channel
                    if binary_index < len(binary_message):
                        g = (g & 0xFE) | int(binary_message[binary_index])
                        binary_index += 1
                    
                    # Modify LSB of blue channel
                    if binary_index < len(binary_message):
                        b = (b & 0xFE) | int(binary_message[binary_index])
                        binary_index += 1
                    
                    modified_pixels.append((r, g, b))
                else:
                    modified_pixels.append(pixel)
            
            # Create new image with modified pixels
            new_img = Image.new('RGB', (width, height))
            new_img.putdata(modified_pixels)
            
            # Save the image
            new_img.save(output_path)
            
            return True, f"Message successfully hidden in {output_path}"
            
        except Exception as e:
            return False, f"Error hiding message: {str(e)}"
    
    def extract_message_from_image(self, image_path, decrypt=True):
        """Extract hidden message from image"""
        try:
            # Load image
            img = Image.open(image_path)
            img = img.convert('RGB')
            
            # Get all pixels
            pixels = list(img.getdata())
            
            # Extract binary message from LSB
            binary_message = ""
            
            for pixel in pixels:
                r, g, b = pixel
                
                # Extract LSB from each channel
                binary_message += str(r & 1)
                binary_message += str(g & 1)
                binary_message += str(b & 1)
            
            # Convert binary to string
            message = self.binary_to_string(binary_message)
            
            # Find the end delimiter
            end_marker = "<<<GHOSTWIRE_END>>>"
            if end_marker in message:
                message = message[:message.find(end_marker)]
            else:
                return False, "No hidden message found or message corrupted"
            
            # Decrypt message if it's encrypted and we have keys
            if decrypt and self.encryption_key:
                message = self.decrypt_message(message)
            
            return True, message
            
        except Exception as e:
            return False, f"Error extracting message: {str(e)}"
    
    def get_image_capacity(self, image_path):
        """Calculate how many characters can be hidden in the image"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            total_pixels = width * height
            # 3 bits per pixel (RGB), 8 bits per character
            max_chars = (total_pixels * 3) // 8
            return max_chars
        except Exception as e:
            return 0

def main():
    parser = argparse.ArgumentParser(description='Ghostwire Steganography - Hide/Extract messages in images')
    
    # Operation mode
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--stealth-image', metavar='IMAGE_PATH',
                      help='Hide message in image (specify image path)')
    group.add_argument('--stealth-extract', metavar='IMAGE_PATH',
                      help='Extract message from image (specify image path)')
    group.add_argument('--stealth-capacity', metavar='IMAGE_PATH',
                      help='Check how many characters can be hidden in image')
    
    # Message and output (for hiding)
    parser.add_argument('--message', help='Message to hide in image')
    parser.add_argument('--output', help='Output image path (for hiding)')
    
    # Encryption keys
    parser.add_argument('--key1', help='First encryption key')
    parser.add_argument('--key2', help='Second encryption key')
    parser.add_argument('--key3', help='Third encryption key')
    
    # Options
    parser.add_argument('--no-encrypt', action='store_true',
                       help='Don\'t encrypt the message (not recommended)')
    
    # Network options (for future integration)
    parser.add_argument('--all', action='store_true', help='Send to all users (future feature)')
    parser.add_argument('--to', help='Send to specific user (future feature)')
    parser.add_argument('--port', type=int, default=2222, help='Port number (future feature)')
    
    args = parser.parse_args()
    
    # Initialize steganography with encryption keys
    stego = GhostwireSteganography(args.key1, args.key2, args.key3)
    
    if args.stealth_image:
        # Hide message in image
        if not args.message:
            print("Error: --message is required when hiding message in image")
            sys.exit(1)
        
        if not args.output:
            print("Error: --output is required when hiding message in image")
            sys.exit(1)
        
        if not os.path.exists(args.stealth_image):
            print(f"Error: Image file {args.stealth_image} not found")
            sys.exit(1)
        
        encrypt = not args.no_encrypt
        success, result = stego.hide_message_in_image(
            args.stealth_image, args.message, args.output, encrypt
        )
        
        if success:
            print(f"✅ {result}")
            if args.key1 and encrypt:
                print("🔒 Message encrypted with provided keys")
            print(f"📁 Steganographic image saved to: {args.output}")
        else:
            print(f"❌ {result}")
            sys.exit(1)
    
    elif args.stealth_extract:
        # Extract message from image
        if not os.path.exists(args.stealth_extract):
            print(f"Error: Image file {args.stealth_extract} not found")
            sys.exit(1)
        
        decrypt = not args.no_encrypt
        success, result = stego.extract_message_from_image(args.stealth_extract, decrypt)
        
        if success:
            print("✅ Message extracted successfully:")
            print("📝 Hidden message:")
            print("-" * 50)
            print(result)
            print("-" * 50)
            if args.key1 and decrypt:
                print("🔓 Message decrypted with provided keys")
        else:
            print(f"❌ {result}")
            sys.exit(1)
    
    elif args.stealth_capacity:
        # Check image capacity
        if not os.path.exists(args.stealth_capacity):
            print(f"Error: Image file {args.stealth_capacity} not found")
            sys.exit(1)
        
        capacity = stego.get_image_capacity(args.stealth_capacity)
        print(f"📊 Image capacity: {capacity} characters")
        print(f"📁 Image: {args.stealth_capacity}")
        
        # Show image info
        try:
            img = Image.open(args.stealth_capacity)
            width, height = img.size
            print(f"🖼️  Dimensions: {width}x{height} pixels")
            print(f"🎨 Mode: {img.mode}")
        except:
            pass

if __name__ == '__main__':
    main()

