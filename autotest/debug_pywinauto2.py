# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess

log_file = open(r"D:\fund_helper\autotest\debug_output.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()

log("="*60)
log("pywinauto Debug Script - Output to File")
log("="*60)

log("\nStep 1: Check if pywinauto is installed...")
try:
    from pywinauto import Application
    from pywinauto.keyboard import send_keys
    from pywinauto import mouse
    log("[OK] pywinauto is installed")
except ImportError as e:
    log(f"[ERROR] pywinauto not installed: {e}")
    log("   Please run: pip install pywinauto")
    sys.exit(1)

log("\nStep 2: Find Edge browser path...")
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
    sys.exit(1)

log("\nStep 3: Start Edge browser with about:blank...")
try:
    import subprocess
    proc = subprocess.Popen([edge_executable, "about:blank"])
    log("[OK] Edge browser started")
    time.sleep(3)
except Exception as e:
    log(f"[ERROR] Failed to start Edge: {e}")
    sys.exit(1)

log("\nStep 4: Connect to Edge window...")
app = None
main_window = None

for attempt in range(5):
    try:
        log(f"  Attempt {attempt + 1}: Connecting by class_name...")
        app = Application(backend='uia').connect(
            class_name="Chrome_WidgetWin_1",
            timeout=5
        )
        log("[OK] Connected by class_name")
        break
    except Exception as e:
        log(f"  Failed: {e}")
        time.sleep(1)

if app is None:
    try:
        log("  Trying to connect by title...")
        app = Application(backend='uia').connect(
            title_re=".*Edge.*",
            timeout=10
        )
        log("[OK] Connected by title")
    except Exception as e:
        log(f"[ERROR] Failed to connect: {e}")
        sys.exit(1)

log("\nStep 5: Get main window...")
try:
    main_window = app.top_window()
    log(f"[OK] Main window title: {main_window.window_text()}")
except Exception as e:
    log(f"[ERROR] Failed to get main window: {e}")
    sys.exit(1)

log("\nStep 6: Print all windows in the app...")
try:
    windows = app.windows()
    log(f"Found {len(windows)} windows")
    for i, win in enumerate(windows):
        try:
            win_title = win.window_text()
            win_class = win.element_info.class_name
            log(f"  Window [{i}]: title='{win_title}', class='{win_class}'")
        except Exception as e:
            log(f"  Window [{i}]: (Cannot get info)")
except Exception as e:
    log(f"[ERROR] Failed to list windows: {e}")

log("\nStep 7: Find all buttons in main window...")
try:
    all_buttons = main_window.descendants(control_type="Button")
    log(f"Found {len(all_buttons)} buttons")
    
    log("\nListing all buttons:")
    for i, btn in enumerate(all_buttons):
        try:
            btn_name = btn.window_text()
            btn_automation_id = ""
            try:
                btn_automation_id = btn.element_info.automation_id
            except:
                pass
            
            log(f"  [{i}] Button: name='{btn_name}', automation_id='{btn_automation_id}'")
            
            if "Settings" in btn_name or "more" in btn_name.lower() or "more" in btn_automation_id.lower():
                log(f"      [ALERT] This may be the Settings button!")
            
            if "Extensions" in btn_name or "extension" in btn_automation_id.lower():
                log(f"      [ALERT] This may be the Extensions icon!")
                
        except Exception as e:
            log(f"  [{i}] Button: (Cannot get info)")
except Exception as e:
    log(f"[ERROR] Failed to find buttons: {e}")

log("\nStep 8: Find all ToolBars...")
try:
    toolbars = main_window.descendants(control_type="ToolBar")
    log(f"Found {len(toolbars)} toolbars")
    
    for i, toolbar in enumerate(toolbars):
        try:
            toolbar_name = toolbar.window_text()
            log(f"\n  ToolBar [{i}]: name='{toolbar_name}'")
            
            toolbar_buttons = toolbar.children(control_type="Button")
            log(f"    Contains {len(toolbar_buttons)} buttons")
            
            for j, btn in enumerate(toolbar_buttons):
                try:
                    btn_name = btn.window_text()
                    log(f"      [{j}] Button: '{btn_name}'")
                except Exception:
                    log(f"      [{j}] Button: (no name)")
        except Exception as e:
            log(f"  ToolBar [{i}]: (Cannot get info)")
except Exception as e:
    log(f"[ERROR] Failed to find toolbars: {e}")

log("\n" + "="*60)
log("Debug Information Collected!")
log("="*60)
log("""
Key Findings:
1. Check the buttons list for:
   - Buttons with "Settings" or "more" in name (Settings and more button)
   - Buttons with "Extensions" in name (Extensions icon)

2. Check the toolbars for browser controls

3. The debug output is saved to: D:\fund_helper\autotest\debug_output.txt
""")

log("\n" + "="*60)
log("Waiting 20 seconds for manual inspection...")
log("="*60)
log("""
Manual Test Steps:
1. Click the three dots (Settings and more) in the browser
2. Hover over "Extensions" to see the submenu
3. Observe what happens

After this, the script will try Alt+F to open the menu automatically.
""")
log_file.flush()

for i in range(20):
    time.sleep(1)
    if i % 5 == 0:
        log(f"  ... {i} seconds passed")

log("\nStep 9: Try Alt+F to open menu...")
try:
    log("  Sending Alt+F...")
    send_keys('%{F}')
    log("  [OK] Alt+F sent")
    time.sleep(2)
    
    log("\nStep 10: Check for new windows/menus...")
    try:
        new_windows = app.windows()
        log(f"  Now found {len(new_windows)} windows")
        
        for i, win in enumerate(new_windows):
            try:
                win_title = win.window_text()
                win_class = win.element_info.class_name
                log(f"    Window [{i}]: title='{win_title}', class='{win_class}'")
                
                menu_items = win.children(control_type="MenuItem")
                if menu_items:
                    log(f"      Contains {len(menu_items)} menu items:")
                    for j, item in enumerate(menu_items):
                        try:
                            item_name = item.window_text()
                            log(f"        [{j}] MenuItem: '{item_name}'")
                            
                            if "Extensions" in item_name:
                                log(f"          [ALERT] Found Extensions menu item!")
                        except Exception:
                            log(f"        [{j}] MenuItem: (no name)")
            except Exception as e:
                log(f"    Window [{i}]: (Cannot get info)")
    except Exception as e:
        log(f"  [ERROR] Failed to check windows: {e}")
        
except Exception as e:
    log(f"  [ERROR] Failed to send Alt+F: {e}")

log("\n" + "="*60)
log("Debug Complete!")
log("="*60)
log(f"Output saved to: D:\\fund_helper\\autotest\\debug_output.txt")
log("\nPlease review the output file to understand:")
log("1. What buttons are available")
log("2. What happens when Alt+F is pressed")
log("3. How to interact with the Extensions menu")

log_file.close()

print("\nPress Enter to close the browser and exit...")
try:
    input()
except:
    pass

try:
    proc.terminate()
    log("Browser closed")
except:
    pass
