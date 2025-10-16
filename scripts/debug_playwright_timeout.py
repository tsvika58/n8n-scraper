#!/usr/bin/env python3
"""
Debug Playwright Timeout Issues

This script tests Playwright connectivity to n8n.io to identify
why workflows are timing out during extraction.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


async def test_basic_connection():
    """Test basic Playwright connection to n8n.io"""
    print("🧪 TEST 1: Basic Playwright Connection")
    print("-" * 60)
    
    try:
        async with async_playwright() as p:
            print("✅ Playwright started successfully")
            
            # Launch browser
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            print("✅ Browser launched")
            
            # Create context and page
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            print("✅ Page created")
            
            # Test n8n.io homepage first
            print("\n🔗 Testing n8n.io homepage...")
            try:
                response = await page.goto('https://n8n.io', timeout=15000, wait_until='domcontentloaded')
                print(f"✅ Homepage loaded: Status {response.status}")
            except PlaywrightTimeout as e:
                print(f"❌ Homepage timeout: {e}")
                return False
            except Exception as e:
                print(f"❌ Homepage error: {e}")
                return False
            
            # Test workflows page
            print("\n🔗 Testing workflows listing page...")
            try:
                response = await page.goto('https://n8n.io/workflows', timeout=15000, wait_until='domcontentloaded')
                print(f"✅ Workflows page loaded: Status {response.status}")
            except PlaywrightTimeout as e:
                print(f"❌ Workflows page timeout: {e}")
                return False
            except Exception as e:
                print(f"❌ Workflows page error: {e}")
                return False
            
            # Test a specific workflow (ID 1)
            print("\n🔗 Testing specific workflow page (ID 1)...")
            test_url = 'https://n8n.io/workflows/1'
            try:
                print(f"   Navigating to: {test_url}")
                response = await page.goto(test_url, timeout=30000, wait_until='domcontentloaded')
                print(f"✅ Workflow page loaded: Status {response.status}")
                
                # Check page content
                title = await page.title()
                print(f"   Page title: {title}")
                
                # Check if page has expected elements
                body_text = await page.inner_text('body')
                if len(body_text) > 100:
                    print(f"   Page content: {len(body_text)} characters")
                else:
                    print(f"   ⚠️  Minimal content: {len(body_text)} characters")
                
            except PlaywrightTimeout as e:
                print(f"❌ Workflow page timeout after 30s: {e}")
                return False
            except Exception as e:
                print(f"❌ Workflow page error: {e}")
                return False
            
            await browser.close()
            print("\n✅ Browser closed successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Playwright initialization failed: {e}")
        return False


async def test_with_different_timeouts():
    """Test with various timeout settings"""
    print("\n\n🧪 TEST 2: Different Timeout Settings")
    print("-" * 60)
    
    timeouts = [10000, 30000, 60000]
    test_url = 'https://n8n.io/workflows/1'
    
    for timeout in timeouts:
        print(f"\n⏱️  Testing with {timeout/1000}s timeout...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                context = await browser.new_context()
                page = await context.new_page()
                
                import time
                start = time.time()
                
                try:
                    response = await page.goto(test_url, timeout=timeout, wait_until='domcontentloaded')
                    elapsed = time.time() - start
                    print(f"   ✅ SUCCESS in {elapsed:.2f}s (Status: {response.status})")
                except PlaywrightTimeout:
                    elapsed = time.time() - start
                    print(f"   ❌ TIMEOUT after {elapsed:.2f}s")
                
                await browser.close()
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")


async def test_network_strategy():
    """Test different network wait strategies"""
    print("\n\n🧪 TEST 3: Network Wait Strategies")
    print("-" * 60)
    
    strategies = [
        ('domcontentloaded', 'DOM Content Loaded'),
        ('load', 'Full Page Load'),
        ('networkidle', 'Network Idle')
    ]
    
    test_url = 'https://n8n.io/workflows/1'
    
    for strategy, description in strategies:
        print(f"\n📡 Testing: {description} ({strategy})...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                context = await browser.new_context()
                page = await context.new_page()
                
                import time
                start = time.time()
                
                try:
                    response = await page.goto(test_url, timeout=30000, wait_until=strategy)
                    elapsed = time.time() - start
                    print(f"   ✅ SUCCESS in {elapsed:.2f}s (Status: {response.status})")
                except PlaywrightTimeout:
                    elapsed = time.time() - start
                    print(f"   ❌ TIMEOUT after {elapsed:.2f}s")
                except Exception as e:
                    print(f"   ❌ ERROR: {e}")
                
                await browser.close()
                
        except Exception as e:
            print(f"   ❌ SETUP ERROR: {e}")


async def test_container_network():
    """Test if container can reach n8n.io at all"""
    print("\n\n🧪 TEST 4: Container Network Connectivity")
    print("-" * 60)
    
    import subprocess
    
    print("🔗 Testing DNS resolution...")
    try:
        result = subprocess.run(
            ['docker', 'exec', 'n8n-scraper-app', 'ping', '-c', '3', 'n8n.io'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Can ping n8n.io")
        else:
            print(f"❌ Cannot ping n8n.io: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Ping test skipped: {e}")
    
    print("\n🔗 Testing HTTP connectivity with curl...")
    try:
        result = subprocess.run(
            ['docker', 'exec', 'n8n-scraper-app', 'curl', '-I', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'https://n8n.io'],
            capture_output=True,
            text=True,
            timeout=10
        )
        status_code = result.stdout.strip()
        if status_code == '200':
            print(f"✅ HTTP request successful: {status_code}")
        else:
            print(f"⚠️  HTTP status: {status_code}")
    except Exception as e:
        print(f"❌ HTTP test failed: {e}")


async def main():
    """Run all diagnostic tests"""
    print("=" * 60)
    print("🔍 PLAYWRIGHT TIMEOUT DIAGNOSTIC")
    print("=" * 60)
    print()
    
    # Test 1: Basic connection
    test1_success = await test_basic_connection()
    
    if not test1_success:
        print("\n⚠️  Basic connection failed. Checking network...")
        await test_container_network()
        return
    
    # Test 2: Different timeouts
    await test_with_different_timeouts()
    
    # Test 3: Network strategies
    await test_network_strategy()
    
    # Test 4: Container network
    await test_container_network()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("\n💡 RECOMMENDATIONS:")
    print("   1. If basic connection works: Increase timeout to 60s+")
    print("   2. If timeouts persist: Use 'domcontentloaded' strategy")
    print("   3. If network fails: Check Docker network settings")
    print("   4. Consider rate limiting if many requests fail")


if __name__ == "__main__":
    asyncio.run(main())






