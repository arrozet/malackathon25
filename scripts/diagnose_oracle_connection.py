#!/usr/bin/env python3
"""
Oracle Connection Diagnostics Script for Production.

This script tests various aspects of Oracle connectivity to help diagnose
connection issues in production environments.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import oracledb
from app.back.config import config


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_environment():
    """Test environment variables and configuration."""
    print_section("1. Environment Configuration")
    
    print("Configuration loaded:")
    for key, value in config.display_config().items():
        print(f"  {key}: {value}")
    
    print("\n✓ Configuration loaded successfully")


def test_wallet_files():
    """Check if wallet files exist and are readable."""
    print_section("2. Wallet Files Check")
    
    wallet_dir = config.TNS_ADMIN
    print(f"Wallet directory: {wallet_dir}")
    
    if not os.path.exists(wallet_dir):
        print(f"✗ ERROR: Wallet directory does not exist!")
        return False
    
    print(f"✓ Wallet directory exists")
    
    required_files = [
        "cwallet.sso",
        "tnsnames.ora",
        "sqlnet.ora"
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = os.path.join(wallet_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✓ {filename} exists ({size} bytes)")
        else:
            print(f"  ✗ {filename} MISSING")
            all_exist = False
    
    if all_exist:
        print("\n✓ All required wallet files present")
        return True
    else:
        print("\n✗ Some wallet files are missing")
        return False


def test_dns_resolution():
    """Test DNS resolution for Oracle Cloud."""
    print_section("3. Network Connectivity")
    
    import socket
    
    host = "adb.eu-madrid-1.oraclecloud.com"
    port = 1522
    
    print(f"Testing DNS resolution for {host}...")
    try:
        ip = socket.gethostbyname(host)
        print(f"✓ DNS resolved to {ip}")
    except socket.gaierror as e:
        print(f"✗ DNS resolution failed: {e}")
        return False
    
    print(f"\nTesting TCP connectivity to {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✓ TCP connection successful")
            return True
        else:
            print(f"✗ TCP connection failed (error code: {result})")
            print(f"  This may indicate a firewall blocking connections to Oracle Cloud")
            return False
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


def test_oracle_connection():
    """Test actual Oracle database connection."""
    print_section("4. Oracle Database Connection")
    
    print("Creating connection pool...")
    try:
        pool = oracledb.create_pool(
            user=config.ORACLE_USER,
            password=config.ORACLE_PASSWORD,
            dsn=config.ORACLE_DSN,
            min=0,
            max=2,
            config_dir=config.TNS_ADMIN,
            wallet_location=config.TNS_ADMIN,
            wallet_password=config.ORACLE_WALLET_PASSWORD,
        )
        print("✓ Connection pool created")
        
        print("\nAcquiring connection from pool...")
        conn = pool.acquire()
        print("✓ Connection acquired")
        
        print("\nExecuting test query...")
        cursor = conn.cursor()
        cursor.execute("SELECT 'Connection successful!' AS result, SYSDATE FROM DUAL")
        result = cursor.fetchone()
        print(f"✓ Query executed: {result[0]} at {result[1]}")
        
        cursor.close()
        pool.release(conn)
        pool.close()
        
        print("\n✓ Oracle connection test PASSED")
        return True
        
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"\n✗ Oracle connection FAILED")
        print(f"  Error: {error_obj.message}")
        print(f"  Error code: {error_obj.code if hasattr(error_obj, 'code') else 'N/A'}")
        
        # Provide specific troubleshooting advice
        error_msg = str(error_obj.message).lower()
        if "dpy-4005" in error_msg or "timeout" in error_msg:
            print("\n  Troubleshooting: Connection timeout")
            print("  - Check if Oracle Cloud firewall allows connections from this IP")
            print("  - Verify network connectivity to adb.eu-madrid-1.oraclecloud.com:1522")
            print("  - Check if wallet files are correctly configured")
        elif "ora-01017" in error_msg or "invalid username" in error_msg:
            print("\n  Troubleshooting: Authentication failed")
            print("  - Verify ORACLE_USER and ORACLE_PASSWORD in .env")
            print("  - Check if user exists in Oracle database")
        elif "wallet" in error_msg:
            print("\n  Troubleshooting: Wallet issue")
            print("  - Verify wallet files are not corrupted")
            print("  - Check ORACLE_WALLET_PASSWORD in .env")
            print("  - Ensure sqlnet.ora points to correct wallet directory")
        
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def main():
    """Run all diagnostic tests."""
    print("\n" + "="*60)
    print("  Oracle Connection Diagnostics - Malackathon 2025")
    print("="*60)
    
    # Run all tests
    tests = [
        ("Environment", test_environment),
        ("Wallet Files", test_wallet_files),
        ("Network", test_dns_resolution),
        ("Oracle Connection", test_oracle_connection),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print_section("Summary")
    
    all_passed = True
    for name in results:
        status = "✓ PASS" if results[name] else "✗ FAIL"
        print(f"  {status} - {name}")
        if not results[name]:
            all_passed = False
    
    if all_passed:
        print("\n✓✓✓ All tests PASSED! Oracle connection is working correctly.")
        return 0
    else:
        print("\n✗✗✗ Some tests FAILED. Review the output above for troubleshooting.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

