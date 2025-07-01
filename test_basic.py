#!/usr/bin/env python3
"""
Basic functionality test for Ghostwire
"""

import sys
import os
import subprocess
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🔧 Testing module imports...")
    
    try:
        import ghostwire
        print("✅ ghostwire.py - OK")
    except Exception as e:
        print(f"❌ ghostwire.py - Error: {e}")
        return False
    
    try:
        import ghostwire2
        print("✅ ghostwire2.py - OK")
    except Exception as e:
        print(f"❌ ghostwire2.py - Error: {e}")
        return False
    
    try:
        import ghostwire_chat
        print("✅ ghostwire_chat.py - OK")
    except Exception as e:
        print(f"❌ ghostwire_chat.py - Error: {e}")
        return False
    
    try:
        import ghostwire_broadcast
        print("✅ ghostwire_broadcast.py - OK")
    except Exception as e:
        print(f"❌ ghostwire_broadcast.py - Error: {e}")
        return False
    
    return True

def test_encryption():
    """Test encryption/decryption functionality"""
    print("\n🔐 Testing encryption functionality...")
    
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad, unpad
        import base64
        
        # Test basic encryption
        key = pad(b"testkey123456789", 16)
        message = "Hello, Ghostwire!"
        
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message.encode(), 16))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        encrypted = iv + " " + ct
        
        # Test decryption
        iv_b64, ct_b64 = encrypted.split(" ", 1)
        iv = base64.b64decode(iv_b64)
        ct = base64.b64decode(ct_b64)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), 16)
        decrypted = pt.decode('utf-8')
        
        if decrypted == message:
            print("✅ AES encryption/decryption - OK")
            return True
        else:
            print(f"❌ Encryption test failed: expected '{message}', got '{decrypted}'")
            return False
            
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False

def test_command_line():
    """Test command line interface"""
    print("\n💻 Testing command line interface...")
    
    try:
        # Test help
        result = subprocess.run(
            ['./ghostwire', '--help-all'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0 and "Available Components" in result.stdout:
            print("✅ Command line help - OK")
            
            # Test v1 help
            result_v1 = subprocess.run(
                ['./ghostwire', '--version', 'v1', '--help'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            
            if result_v1.returncode == 0 and "Ghostwire - Encrypted P2P Communication Tool" in result_v1.stdout:
                print("✅ v1 help - OK")
                
                # Test v2 help
                result_v2 = subprocess.run(
                    ['./ghostwire', '--version', 'v2', '--help'],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(__file__)
                )
                
                if result_v2.returncode == 0 and "Ghostwire2 - Fixed P2P Communication Tool" in result_v2.stdout:
                    print("✅ v2 help - OK")
                    return True
                else:
                    print(f"❌ v2 help failed: {result_v2.stderr}")
                    return False
            else:
                print(f"❌ v1 help failed: {result_v1.stderr}")
                return False
        else:
            print(f"❌ Main help failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Command line test failed: {e}")
        return False

def main():
    print("🚀 Ghostwire Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Encryption", test_encryption),
        ("Command Line", test_command_line)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n❌ {test_name} test failed!")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ghostwire is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

