# -*- coding: utf-8 -*-
import os
import sys
import time
import asyncio

async def main():
    print("="*60)
    print("Testing Playwright Extension Support")
    print("="*60)
    
    log_file = open(r"D:\fund_helper\autotest\debug_playwright_extension.txt", "w", encoding="utf-8")
    
    def log(msg):
        print(msg)
        log_file.write(str(msg) + "\n")
        log_file.flush()
    
    log("\nStep 1: Checking if playwright is installed...")
    try:
        from playwright.async_api import async_playwright
        log("[OK] playwright is installed")
    except ImportError as e:
        log(f"[ERROR] playwright not installed: {e}")
        return
    
    log("\nStep 2: Finding Edge browser...")
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    
    edge_executable = None
    for path in edge_paths:
        if os.path.exists(path):
            edge_executable = path
            break
    
    if edge_executable:
        log(f"[OK] Found Edge: {edge_executable}")
    else:
        log("[ERROR] Edge browser not found")
        return
    
    extension_path = r"D:\fund_helper\funds\dist-zip\choose-funds-v2.5.2"
    log(f"\nStep 3: Extension path: {extension_path}")
    
    if os.path.exists(extension_path):
        log("[OK] Extension path exists")
        
        manifest_path = os.path.join(extension_path, "manifest.json")
        if os.path.exists(manifest_path):
            import json
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            log(f"  Extension name: {manifest.get('name', 'N/A')}")
            log(f"  Extension version: {manifest.get('version', 'N/A')}")
            log(f"  Manifest version: {manifest.get('manifest_version', 'N/A')}")
            
            if 'browser_action' in manifest:
                popup = manifest['browser_action'].get('default_popup', 'N/A')
                log(f"  Popup page: {popup}")
    else:
        log("[ERROR] Extension path does not exist")
        return
    
    log("\n" + "="*60)
    log("Starting browser with extension...")
    log("="*60)
    
    async with async_playwright() as p:
        log("\nStep 4: Launching browser with extension...")
        
        args = [
            f"--disable-extensions-except={extension_path}",
            f"--load-extension={extension_path}",
        ]
        
        log(f"  Launch arguments:")
        for arg in args:
            log(f"    {arg}")
        
        browser = await p.chromium.launch(
            executable_path=edge_executable,
            headless=False,
            args=args,
        )
        
        log("[OK] Browser launched")
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        
        log("[OK] Context created")
        
        page = await context.new_page()
        
        log("[OK] Page created")
        
        log("\nStep 5: Checking pages...")
        pages = context.pages
        log(f"  Found {len(pages)} pages")
        
        for i, p_page in enumerate(pages):
            try:
                log(f"    Page [{i}]: {p_page.url}")
            except Exception as e:
                log(f"    Page [{i}]: (Cannot get URL: {e})")
        
        log("\nStep 6: Navigating to extensions page...")
        try:
            await page.goto("edge://extensions/", wait_until="networkidle")
            await asyncio.sleep(2)
            log("[OK] Navigated to extensions page")
        except Exception as e:
            log(f"[WARNING] Failed to navigate to extensions page: {e}")
        
        log("\nStep 7: Checking for extension pages...")
        pages = context.pages
        log(f"  Found {len(pages)} pages")
        
        extension_pages = []
        for i, p_page in enumerate(pages):
            try:
                url = p_page.url
                log(f"    Page [{i}]: {url}")
                
                if url.startswith("chrome-extension://"):
                    log(f"      [ALERT] This is an extension page!")
                    extension_pages.append(p_page)
                    
                    if "popup" in url.lower() or "fund" in url.lower():
                        log(f"      [ALERT] This may be the popup page!")
            except Exception as e:
                log(f"    Page [{i}]: (Cannot get URL: {e})")
        
        log(f"\n  Found {len(extension_pages)} extension pages")
        
        log("\nStep 8: Waiting and checking for new pages...")
        log("  The extension may open pages automatically")
        log("  We'll wait 5 seconds and check again...")
        
        for attempt in range(5):
            await asyncio.sleep(1)
            
            pages = context.pages
            log(f"    After {attempt + 1} second(s): {len(pages)} pages")
            
            for i, p_page in enumerate(pages):
                try:
                    url = p_page.url
                    if url.startswith("chrome-extension://"):
                        log(f"      Page [{i}]: {url}")
                except:
                    pass
        
        log("\n" + "="*60)
        log("Analysis of Extension Access Methods")
        log("="*60)
        log("""
Key Findings:
1. The extension is loaded via --load-extension parameter
2. The extension has a popup page: popup/popup.html
3. We need to find a way to open this popup page

Possible Methods to Open Extension Popup:

Method 1: Direct URL Access (if we know the extension ID)
  - URL format: chrome-extension://<extension-id>/popup/popup.html
  - Problem: We don't know the extension ID

Method 2: Find extension pages automatically
  - Check all pages for chrome-extension:// URLs
  - Problem: The popup page may not be open yet

Method 3: Manual Operation (Most Reliable)
  - Instruct the user to click the extension icon
  - Script waits for the popup page to appear
  - This is what we'll use

Method 4: Use Playwright's Extension API
  - Playwright has some extension support
  - Let's check if we can get extension info
""")
        
        log("\nStep 9: Checking browser contexts and background pages...")
        try:
            contexts = browser.contexts
            log(f"  Found {len(contexts)} contexts")
            
            for i, ctx in enumerate(contexts):
                log(f"\n    Context [{i}]:")
                
                pages = ctx.pages
                log(f"      Pages: {len(pages)}")
                
                for j, p_page in enumerate(pages):
                    try:
                        url = p_page.url
                        log(f"        Page [{j}]: {url}")
                    except:
                        log(f"        Page [{j}]: (Cannot get URL)")
                
                try:
                    service_workers = ctx.service_workers
                    log(f"      Service Workers: {len(service_workers)}")
                    
                    for j, sw in enumerate(service_workers):
                        try:
                            log(f"        ServiceWorker [{j}]: {sw.url}")
                        except:
                            pass
                except Exception as e:
                    log(f"      Service Workers: (Cannot access: {e})")
                
        except Exception as e:
            log(f"  [ERROR] Failed to check contexts: {e}")
        
        log("\n" + "="*60)
        log("Recommended Approach")
        log("="*60)
        log("""
Based on this analysis, here's what we'll do:

1. Use Playwright to launch the browser and load the extension
   - This works reliably via --load-extension parameter

2. For opening the extension popup:
   - We cannot reliably automate clicking the extension icon
   - pywinauto has issues with Edge's multi-process architecture
   - We'll provide clear manual instructions

3. The test script will:
   - Launch the browser
   - Navigate to extensions page to verify extension is loaded
   - Instruct the user to click the extension icon
   - Wait for the popup page to appear
   - Continue with the tests

4. Key insight:
   - The extension's popup page is: popup/popup.html
   - When the user clicks the extension icon, this page opens
   - We can detect this page by its URL pattern:
     * chrome-extension://*/popup/popup.html
     * Contains "popup" or "fund" in the URL

This approach is reliable and works with the limitations of:
- Playwright's extension support
- pywinauto's issues with Edge's multi-process architecture
- Browser security restrictions
""")
        
        log("\n" + "="*60)
        log("Test Script Design")
        log("="*60)
        log("""
The updated test script will:

1. Setup Phase:
   - Launch Edge browser
   - Load extension via --load-extension parameter
   - Connect pywinauto (but don't rely on it for critical operations)

2. Verification Phase:
   - Navigate to edge://extensions/
   - Verify the extension is listed
   - Take a screenshot

3. Extension Opening Phase:
   - Display clear instructions to the user
   - Instruct to click the extension icon
   - Wait for the popup page to appear (up to 120 seconds)
   - Detect chrome-extension://*/popup/popup.html URLs

4. Testing Phase:
   - Once popup is detected, continue with tests
   - Test fund comparison functionality
   - Generate bug reports if issues found

5. Cleanup Phase:
   - Close browser
   - Generate test summary

This design is:
- Reliable (works within known limitations)
- User-friendly (clear instructions)
- Robust (handles edge cases)
""")
        
        log("\n" + "="*60)
        log("Keeping Browser Open for Manual Inspection")
        log("="*60)
        log("""
The browser will remain open for 30 seconds.
You can manually test:
1. Click the extension icon (puzzle shape) in the toolbar
2. Select "自选基金助手" from the list
3. Observe what happens

After this, we'll update the test scripts with the recommended approach.
""")
        
        log_file.flush()
        
        for i in range(30):
            await asyncio.sleep(1)
            if i % 10 == 0 and i > 0:
                log(f"  ... {i} seconds passed")
                
                pages = context.pages
                log(f"      Current pages: {len(pages)}")
                for j, p_page in enumerate(pages):
                    try:
                        url = p_page.url
                        log(f"        [{j}]: {url}")
                    except:
                        pass
        
        log("\nClosing browser...")
        await browser.close()
        log("[OK] Browser closed")
    
    log_file.close()
    print("\nDebug complete!")
    print(f"Output saved to: D:\\fund_helper\\autotest\\debug_playwright_extension.txt")

if __name__ == "__main__":
    asyncio.run(main())
