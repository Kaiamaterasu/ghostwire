#!/usr/bin/env python3
"""
Test script for command-line only Ghostwire
"""

import subprocess
import time
import sys
import os

def test_command_line_only():
    """Test the new command-line only functionality"""
    print("🧪 Testing Command-Line Only Ghostwire...")
    
    # Clean up any existing config files
    os.system('rm -f /tmp/ghostwire_config.json /tmp/ghostwire_data.json')
    
    # Test help
    result = subprocess.run(['./ghostwire', '--help'], capture_output=True, text=True, cwd='/home/failsafe/ghostwire')
    if result.returncode == 0 and "Command-Line Only P2P Communication Tool" in result.stdout:
        print("✅ Help command works")
    else:
        print("❌ Help command failed")
        return False
    
    # Test error without keys - should show error when no keys provided
    result = subprocess.run(['./ghostwire'], capture_output=True, text=True, cwd='/home/failsafe/ghostwire')
    if "ERROR" in result.stdout and "key1" in result.stdout:
        print("✅ Shows error when no keys provided")
    else:
        print("❌ Should show error when no keys provided")
        return False
    
    # Test usage info with keys (should show usage)
    result = subprocess.run(['./ghostwire', '--key1', 'test1', '--key2', 'test2', '--key3', 'test3'], 
                          capture_output=True, text=True, cwd='/home/failsafe/ghostwire')
    if "Command Line Usage" in result.stdout:
        print("✅ Usage info displayed correctly when keys provided without action")
    else:
        print("❌ Usage info not displayed")
        return False
    
    # Test error when trying to send without keys
    result = subprocess.run(['./ghostwire', '--send', 'test', '--user', 'test', '--all'], 
                          capture_output=True, text=True, cwd='/home/failsafe/ghostwire')
    if "ERROR" in result.stdout and ("keys" in result.stdout or "connection" in result.stdout or "Connection refused" in result.stdout):
        print("✅ Proper error when trying to send without keys")
    else:
        print(f"❌ Should show error when sending without keys. Got: {result.stdout}")
        return False
    
    print("✅ All command-line tests passed!")
    return True

def test_server_startup():
    """Test server startup and shutdown"""
    print("\n🖥️ Testing Server Startup...")
    
    # Start server in background
    server_proc = subprocess.Popen([
        './ghostwire', '--enable', 
        '--key1', 'test1', '--key2', 'test2', '--key3', 'test3',
        '--alias', 'test-room', '--port', '5555'
    ], cwd='/home/failsafe/ghostwire', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give it time to start
    time.sleep(2)
    
    # Check if it's running
    if server_proc.poll() is None:
        print("✅ Server started successfully")
        
        # Test list users (should work even with no users)
        result = subprocess.run([
            './ghostwire', '--list-all', '--port', '5555'
        ], capture_output=True, text=True, cwd='/home/failsafe/ghostwire')
        
        if result.returncode == 0:
            print("✅ List users command works")
        else:
            print(f"❌ List users failed: {result.stderr}")
        
        # Test sending message to all (should work even with no other users)
        result = subprocess.run([
            './ghostwire', '--send', 'Hello World', 
            '--user', 'tester', '--all', '--port', '5555'
        ], capture_output=True, text=True, cwd='/home/failsafe/ghostwire')
        
        if result.returncode == 0 and "Message sent to all" in result.stdout:
            print("✅ Send message to all works")
        else:
            print(f"❌ Send message failed: {result.stderr}")
        
        # Terminate server
        server_proc.terminate()
        server_proc.wait()
        print("✅ Server stopped successfully")
        return True
    else:
        print("❌ Server failed to start")
        print(f"Error: {server_proc.stderr.read().decode()}")
        return False

def main():
    print("🚀 Testing Command-Line Only Ghostwire")
    print("=" * 50)
    
    tests = [
        ("Command Line Interface", test_command_line_only),
        ("Server Startup", test_server_startup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔧 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed!")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Command-line only Ghostwire is working correctly.")
        print("\n📝 Usage examples:")
        print("# Start server:")
        print("./ghostwire --enable --key1 57575 --key2 6464 --key3 7766 --alias my-room")
        print("\n# Send to all:")
        print("./ghostwire --send 'Hello everyone' --user myname --all")
        print("\n# Send private:")
        print("./ghostwire --send 'Secret message' --user myname --to targetuser")
        print("\n# List users:")
        print("./ghostwire --list-all")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

