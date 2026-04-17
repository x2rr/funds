# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import psutil

log_file = open(r"D:\fund_helper\autotest\debug_output2.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()

log("="*60)
log("pywinauto Debug Script - Using Process ID")
log("="*60)

log("\nStep 1: Check if pywinauto is installed...")
try:
    from pywinauto import Application
    from pywinauto.keyboard import send_keys
    from pywinauto import mouse
    log("[OK] pywinauto is installed")
except ImportError as e:
    log(f"[ERROR] pywinauto not installed: {e}")
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

log("\nStep 3: List running Edge processes before starting new one...")
try:
    edge_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'msedge' in proc.info['name'].lower():
            edge_processes.append(proc)
            log(f"  Found Edge process: PID={proc.info['pid']}, name={proc.info['name']}")
    
    log(f"\n  Total Edge processes: {len(edge_processes)}")
except Exception as e:
    log(f"  [WARNING] Failed to list processes: {e}")

log("\nStep 4: Start a NEW Edge browser with about:blank...")
try:
    proc = subprocess.Popen([edge_executable, "about:blank", "--new-window"])
    new_pid = proc.pid
    log(f"[OK] New Edge browser started with PID: {new_pid}")
    
    log("\n  Waiting for browser to initialize...")
    time.sleep(5)
    
    log("\nStep 5: List Edge processes again to find the new one...")
    edge_processes2 = []
    for proc2 in psutil.process_iter(['pid', 'name']):
        if proc2.info['name'] and 'msedge' in proc2.info['name'].lower():
            edge_processes2.append(proc2)
            log(f"  Edge process: PID={proc2.info['pid']}, name={proc2.info['name']}")
    
    log(f"\n  Total Edge processes now: {len(edge_processes2)}")
    
except Exception as e:
    log(f"[ERROR] Failed to start Edge: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

log("\nStep 6: Connect to the NEW Edge window using PID...")
app = None
main_window = None

for attempt in range(5):
    try:
        log(f"  Attempt {attempt + 1}: Connecting to PID {new_pid}...")
        app = Application(backend='uia').connect(process=new_pid)
        log("[OK] Connected to new Edge process!")
        break
    except Exception as e:
        log(f"  Failed: {e}")
        time.sleep(2)

if app is None:
    log("[ERROR] Failed to connect to new Edge process")
    sys.exit(1)

log("\nStep 7: Get main window...")
try:
    windows = app.windows()
    log(f"  Found {len(windows)} windows in the process")
    
    for i, win in enumerate(windows):
        try:
            win_title = win.window_text()
            win_class = win.element_info.class_name
            win_visible = win.is_visible()
            log(f"    Window [{i}]: title='{win_title}', class='{win_class}', visible={win_visible}")
            
            if win_visible and ("Edge" in win_title or "about:blank" in win_title):
                main_window = win
                log(f"    [SELECTED] This is the main window!")
        except Exception as e:
            log(f"    Window [{i}]: (Cannot get info: {e})")
    
    if main_window is None:
        log("  Trying top_window()...")
        main_window = app.top_window()
        log(f"  top_window() title: {main_window.window_text()}")
        
except Exception as e:
    log(f"[ERROR] Failed to get main window: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

log("\nStep 8: Find all buttons in main window...")
try:
    all_buttons = main_window.descendants(control_type="Button")
    log(f"Found {len(all_buttons)} buttons")
    
    log("\nListing all buttons (first 50):")
    for i, btn in enumerate(all_buttons[:50]):
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
            log(f"  [{i}] Button: (Cannot get info: {e})")
except Exception as e:
    log(f"[ERROR] Failed to find buttons: {e}")

log("\nStep 9: Find all ToolBars...")
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
            log(f"  ToolBar [{i}]: (Cannot get info: {e})")
except Exception as e:
    log(f"[ERROR] Failed to find toolbars: {e}")

log("\n" + "="*60)
log("Debug Information Collected!")
log("="*60)
log("""
Now testing Alt+F to open the menu...
This will show us what menu items are available.
""")
log_file.flush()

log("\nStep 10: Try Alt+F to open menu...")
try:
    log("  Activating main window first...")
    main_window.set_focus()
    time.sleep(1)
    
    log("  Sending Alt+F...")
    send_keys('%{F}')
    log("  [OK] Alt+F sent")
    time.sleep(2)
    
    log("\nStep 11: Check for new windows/menus...")
    try:
        all_windows = app.windows()
        log(f"  Now found {len(all_windows)} windows in process")
        
        for i, win in enumerate(all_windows):
            try:
                win_title = win.window_text()
                win_class = win.element_info.class_name
                win_visible = win.is_visible()
                log(f"\n    Window [{i}]: title='{win_title}', class='{win_class}', visible={win_visible}")
                
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
                log(f"    Window [{i}]: (Cannot get info: {e})")
        
        log("\n  Checking all windows from all processes...")
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        
        all_desktop_windows = desktop.windows()
        log(f"  Found {len(all_desktop_windows)} windows on desktop")
        
        for i, win in enumerate(all_desktop_windows):
            try:
                win_title = win.window_text()
                if "Menu" in win_title or "menu" in win_title.lower() or not win_title:
                    win_class = win.element_info.class_name
                    log(f"\n    Potential Menu [{i}]: title='{win_title}', class='{win_class}'")
                    
                    try:
                        children = win.children()
                        log(f"      Has {len(children)} children")
                        
                        for j, child in enumerate(children):
                            try:
                                child_type = child.element_info.control_type
                                child_name = child.window_text()
                                log(f"        [{j}] {child_type}: '{child_name}'")
                            except:
                                pass
                    except:
                        pass
            except:
                pass
                
    except Exception as e:
        log(f"  [ERROR] Failed to check windows: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    log(f"  [ERROR] Failed to send Alt+F: {e}")

log("\n" + "="*60)
log("Debug Complete!")
log("="*60)
log(f"Output saved to: D:\\fund_helper\\autotest\\debug_output2.txt")
log("\nPlease review the output file to understand:")
log("1. What buttons are available in the browser")
log("2. What happens when Alt+F is pressed")
log("3. How to interact with the Extensions menu")

log_file.close()

print("\nPress Enter to close the browser and exit...")
try:
    input()
except:
    pass

try:
    for proc2 in psutil.process_iter(['pid', 'name']):
        if proc2.info['pid'] == new_pid:
            proc2.terminate()
            log("Browser closed")
            break
except:
    pass
