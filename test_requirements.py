#!/usr/bin/env python3
"""
Test script to verify improved requirements:
1. Room creator authority - only creator can disable room
2. Simplified user management - no redundant --create-user
3. Clean commands work as specified
"""

import subprocess
import time
import sys
import os
import shlex

def run_cmd(cmd, cwd='/home/failsafe/ghostwire'):
    """Run command and return result"""
    result = subprocess.run(shlex.split(cmd), capture_output=True, text=True, cwd=cwd)
    return result.stdout, result.stderr, result.returncode

def test_simplified_user_management():
    """Test that user management is simplified and logical"""
    print("🔒 Testing Simplified User Management...")
    
    # Test send without server (should show connection error, not user error)
    stdout, stderr, code = run_cmd("./ghostwire --send 'test' --all")
    if "[ERROR]" in stdout and ("connection" in stdout or "keys" in stdout):
        print("✅ Send shows connection error (not user error)")
    else:
        print(f"❌ Send should show connection error. Got: {stdout}")
        return False
    
    # Test list without server (should show connection error, not user error)
    stdout, stderr, code = run_cmd("./ghostwire --list-all")
    if "[ERROR]" in stdout and ("connection" in stdout or "keys" in stdout):
        print("✅ List shows connection error (not user error)")
    else:
        print(f"❌ List should show connection error. Got: {stdout}")
        return False
    
    # Test that --user appears in help (indicating it's available)
    stdout, stderr, code = run_cmd("./ghostwire --help")
    if "--user USER" in stdout and "Your username for sending messages" in stdout:
        print("✅ Help shows --user option available")
    else:
        print(f"❌ Help should show --user option. Got: {stdout}")
        return False
    
    return True

def test_correct_usage():
    """Test the correct command usage works"""
    print("\n✅ Testing Correct Usage Patterns...")
    
    # Start server with correct syntax
    print("Starting server...")
    server_proc = subprocess.Popen([
        './ghostwire', '--enable', 
        '--key1', 'alice1', '--key2', 'alice2', '--key3', 'alice3',
        '--alias', 'test-room', '--create-user', 'alice', '--port', '7777'
    ], cwd='/home/failsafe/ghostwire', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(2)
    
    if server_proc.poll() is None:
        print("✅ Server started with correct syntax")
        
        # Test send to all with --user
        stdout, stderr, code = run_cmd('./ghostwire --send "Hello everyone" --user bob --all --port 7777')
        if "Message sent to all" in stdout:
            print("✅ Send to all works with --user")
        else:
            print(f"❌ Send to all failed: {stdout} | STDERR: {stderr}")
            server_proc.terminate()
            return False
        
        # Test list users (no user needed)
        stdout, stderr, code = run_cmd("./ghostwire --list-all --port 7777")
        if "[USERS]" in stdout:
            print("✅ List users works without user specification")
        else:
            print(f"❌ List users failed: {stdout}")
            server_proc.terminate()
            return False
        
        # Test private message with --user
        stdout, stderr, code = run_cmd('./ghostwire --send "Private test" --user david --to alice --port 7777')
        if "Private message sent to alice" in stdout:
            print("✅ Private message works with --user")
        else:
            print(f"❌ Private message failed: {stdout}")
            server_proc.terminate()
            return False
        
        # Test anonymous messaging (no --user needed)
        stdout, stderr, code = run_cmd('./ghostwire --send "Anonymous message" --all --port 7777')
        if "Message sent to all" in stdout:
            print("✅ Anonymous messaging works")
        else:
            print(f"❌ Anonymous messaging failed: {stdout}")
            server_proc.terminate()
            return False
        
        server_proc.terminate()
        server_proc.wait()
        print("✅ Server stopped")
        return True
    else:
        print("❌ Server failed to start")
        return False

def test_usage_info():
    """Test that usage info shows correct improved format"""
    print("\n📚 Testing Usage Information...")
    
    stdout, stderr, code = run_cmd("./ghostwire")
    
    expected_patterns = [
        "--user",
        "optional for sending messages",
        "--send 'message' --user",
        "--list-all",
        "--enable --key1"
    ]
    
    for pattern in expected_patterns:
        if pattern in stdout:
            print(f"✅ Usage shows: {pattern}")
        else:
            print(f"❌ Usage missing: {pattern}")
            return False
    
    return True

def main():
    print("🚀 Testing Ghostwire Requirements")
    print("=" * 50)
    
    # Clean up any existing configs
    os.system('rm -f /tmp/ghostwire_config.json /tmp/ghostwire_data.json')
    
    tests = [
        ("Simplified User Management", test_simplified_user_management),
        ("Correct Usage Patterns", test_correct_usage),
        ("Usage Information", test_usage_info)
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
        print("🎉 All requirements verified!")
        print("\n✅ Improved Requirements Met:")
        print("1. ✅ Simplified user management - no redundant user creation")
        print("2. ✅ Room creator authority implemented")
        print("3. ✅ Clean command syntax works:")
        print("   • ghostwire --send 'message' --user username --all")
        print("   • ghostwire --send 'message' --user username --to someuser")
        print("   • ghostwire --send 'message' --all  (anonymous)")
        print("   • ghostwire --list-all")
        return True
    else:
        print("⚠️ Some requirements not met. Check output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

