#!/usr/bin/env python3
"""
Test script for Ghostwire Steganography Features
Demonstrates hiding and extracting messages from images
"""

import subprocess
import os
from PIL import Image

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_test_images():
    """Create test images of different sizes"""
    print("🖼️  Creating test images...")
    
    # Small image
    img_small = Image.new('RGB', (50, 50), color='red')
    img_small.save('small_test.png')
    
    # Medium image  
    img_medium = Image.new('RGB', (200, 200), color='green')
    img_medium.save('medium_test.png')
    
    # Large image
    img_large = Image.new('RGB', (500, 500), color='blue')
    img_large.save('large_test.png')
    
    print("✅ Test images created: small_test.png, medium_test.png, large_test.png")

def test_steganography():
    """Test steganography functionality"""
    print("\n🔬 Testing Ghostwire Steganography Features")
    print("=" * 60)
    
    # Create test images
    create_test_images()
    
    # Test 1: Basic functionality with encryption
    print("\n📋 Test 1: Hide and extract encrypted message")
    message1 = "This is a secret encrypted message!"
    
    success, output, error = run_command(
        f'./ghostwire --stealth-image medium_test.png --message "{message1}" --output encrypted_stealth.png --key1 111 --key2 222 --key3 333'
    )
    
    if success:
        print("✅ Message hidden with encryption")
        print(output.strip())
        
        # Extract the message
        success, output, error = run_command(
            './ghostwire --stealth-extract encrypted_stealth.png --key1 111 --key2 222 --key3 333'
        )
        
        if success:
            print("✅ Message extracted successfully")
            print(output.strip())
        else:
            print("❌ Failed to extract message")
            print(error)
    else:
        print("❌ Failed to hide message")
        print(error)
    
    # Test 2: Unencrypted message
    print("\n📋 Test 2: Hide and extract unencrypted message")
    message2 = "This is an unencrypted message"
    
    success, output, error = run_command(
        f'./ghostwire --stealth-image medium_test.png --message "{message2}" --output unencrypted_stealth.png'
    )
    
    if success:
        print("✅ Unencrypted message hidden")
        
        # Extract the message
        success, output, error = run_command(
            './ghostwire --stealth-extract unencrypted_stealth.png'
        )
        
        if success:
            print("✅ Unencrypted message extracted")
            print(output.strip())
        else:
            print("❌ Failed to extract unencrypted message")
    else:
        print("❌ Failed to hide unencrypted message")
    
    # Test 3: Check image capacities
    print("\n📋 Test 3: Check image capacities")
    for img_name in ['small_test.png', 'medium_test.png', 'large_test.png']:
        success, output, error = run_command(f'./ghostwire --stealth-capacity {img_name}')
        if success:
            print(f"📊 {img_name}:")
            print(output.strip())
        else:
            print(f"❌ Failed to check capacity for {img_name}")
    
    # Test 4: Long message
    print("\n📋 Test 4: Hide long message")
    long_message = "This is a very long message that tests the capacity of the steganography system. " * 10
    
    success, output, error = run_command(
        f'./ghostwire --stealth-image large_test.png --message "{long_message}" --output long_message_stealth.png --key1 999 --key2 888 --key3 777'
    )
    
    if success:
        print("✅ Long message hidden successfully")
        
        # Extract the long message
        success, output, error = run_command(
            './ghostwire --stealth-extract long_message_stealth.png --key1 999 --key2 888 --key3 777'
        )
        
        if success:
            print("✅ Long message extracted successfully")
            extracted = output.split('Hidden message:')[1].split('--------------------------------------------------')[1].strip()
            if len(extracted) > 100:
                print(f"📝 Message length: {len(extracted)} characters")
                print(f"📝 First 100 chars: {extracted[:100]}...")
            else:
                print(f"📝 Full message: {extracted}")
        else:
            print("❌ Failed to extract long message")
    else:
        print("❌ Failed to hide long message (image too small?)")
        print(error)
    
    # Test 5: Wrong decryption keys
    print("\n📋 Test 5: Test wrong decryption keys")
    success, output, error = run_command(
        './ghostwire --stealth-extract encrypted_stealth.png --key1 wrong --key2 keys --key3 here'
    )
    
    if success:
        print("🔍 Extraction with wrong keys:")
        print(output.strip())
    else:
        print("❌ Failed extraction with wrong keys")
    
    print("\n🎉 Steganography testing completed!")
    print("\n📁 Generated files:")
    for filename in ['encrypted_stealth.png', 'unencrypted_stealth.png', 'long_message_stealth.png']:
        if os.path.exists(filename):
            print(f"  - {filename}")

if __name__ == '__main__':
    test_steganography()

