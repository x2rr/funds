# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess

log_file = open(r"D:\fund_helper\autotest\debug_output4.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()

log("="*60)
log("pywinauto Debug Script - Find Windows via Desktop")
log("="*60)

log("\nStep 1: Check if pywinauto is installed...")
try:
    from pywinauto import Application
    from pywinauto.keyboard import send_keys
    from pywinauto import Desktop
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

log("\nStep 3: List Edge windows before starting new one...")
desktop = Desktop(backend="uia")

try:
    all_windows = desktop.windows()
    log(f"  Found {len(all_windows)} windows on desktop")
    
    edge_windows_before = []
    for i, win in enumerate(all_windows):
        try:
            win_title = win.window_text()
            win_class = win.element_info.class_name
            
            if "Edge" in win_title or "Chrome_WidgetWin" in win_class:
                log(f"    Edge Window [{i}]: title='{win_title}', class='{win_class}'")
                edge_windows_before.append(win)
        except:
            pass
    
    log(f"  Found {len(edge_windows_before)} Edge windows before")
except Exception as e:
    log(f"  [ERROR] Failed to list windows: {e}")

log("\nStep 4: Start a NEW Edge browser...")
try:
    log(f"  Starting: {edge_executable} about:blank --new-window")
    proc = subprocess.Popen([edge_executable, "about:blank", "--new-window"])
    log("[OK] Edge started")
    
    log("\n  Waiting for new window to appear (up to 15 seconds)...")
    new_edge_window = None
    
    for attempt in range(15):
        time.sleep(1)
        
        try:
            all_windows = desktop.windows()
            edge_windows_now = []
            
            for i, win in enumerate(all_windows):
                try:
                    win_title = win.window_text()
                    win_class = win.element_info.class_name
                    
                    if "Edge" in win_title or "Chrome_WidgetWin" in win_class:
                        edge_windows_now.append(win)
                except:
                    pass
            
            log(f"    Attempt {attempt + 1}: Found {len(edge_windows_now)} Edge windows")
            
            if len(edge_windows_now) > len(edge_windows_before):
                log("      New window detected!")
                
                for win in edge_windows_now:
                    try:
                        win_title = win.window_text()
                        is_new = True
                        
                        for old_win in edge_windows_before:
                            try:
                                old_title = old_win.window_text()
                                if win_title == old_title:
                                    is_new = False
                                    break
                            except:
                                pass
                        
                        if is_new:
                            new_edge_window = win
                            log(f"      [FOUND] New window: title='{win_title}'")
                            break
                    except:
                        pass
                
                if new_edge_window:
                    break
        except Exception as e:
            log(f"    Error: {e}")
    
    if new_edge_window is None:
        log("\n  Could not find new window by title difference")
        log("  Trying to find any visible Edge window...")
        
        all_windows = desktop.windows()
        for i, win in enumerate(all_windows):
            try:
                win_title = win.window_text()
                win_class = win.element_info.class_name
                win_visible = win.is_visible()
                
                if win_visible and ("Edge" in win_title or "Chrome_WidgetWin" in win_class):
                    log(f"    Candidate [{i}]: title='{win_title}', class='{win_class}'")
                    new_edge_window = win
                    break
            except:
                pass
    
    if new_edge_window is None:
        log("[ERROR] Could not find new Edge window")
        sys.exit(1)
        
except Exception as e:
    log(f"[ERROR] Failed to start Edge: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

log("\nStep 5: Get process ID from the new window...")
try:
    new_window_pid = new_edge_window.element_info.process_id
    log(f"[OK] New window PID: {new_window_pid}")
    
    log("\nStep 6: Connect to the process...")
    app = Application(backend='uia').connect(process=new_window_pid)
    log("[OK] Connected to the process")
    
    log("\nStep 7: Get main window from app...")
    main_window = app.top_window()
    log(f"[OK] Main window title: {main_window.window_text()}")
    
except Exception as e:
    log(f"[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()

log("\nStep 8: Set focus to main window...")
try:
    main_window.set_focus()
    log("[OK] Focus set")
    time.sleep(1)
except Exception as e:
    log(f"[WARNING] Failed to set focus: {e}")

log("\nStep 9: Find all buttons in main window...")
settings_button = None
extensions_button = None

try:
    all_buttons = main_window.descendants(control_type="Button")
    log(f"Found {len(all_buttons)} buttons")
    
    log("\nListing all buttons (first 70):")
    for i, btn in enumerate(all_buttons[:70]):
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
                settings_button = btn
            
            if "Extensions" in btn_name or "extension" in btn_automation_id.lower():
                log(f"      [ALERT] This may be the Extensions icon!")
                extensions_button = btn
                
        except Exception as e:
            log(f"  [{i}] Button: (Cannot get info: {e})")
except Exception as e:
    log(f"[ERROR] Failed to find buttons: {e}")

log("\nStep 10: Try Alt+F to open menu...")
try:
    log("  Setting focus...")
    main_window.set_focus()
    time.sleep(0.5)
    
    log("  Sending Alt+F...")
    send_keys('%{F}')
    log("  [OK] Alt+F sent")
    time.sleep(2)
    
    log("\nStep 11: Check for menu windows...")
    menu_found = False
    extensions_item = None
    
    all_windows = desktop.windows()
    log(f"  Found {len(all_windows)} windows on desktop")
    
    for i, win in enumerate(all_windows):
        try:
            win_title = win.window_text()
            win_class = win.element_info.class_name
            
            is_menu = False
            if "Menu" in win_title or "menu" in win_title.lower():
                is_menu = True
            if not win_title:
                children = win.children()
                if len(children) > 0:
                    for child in children:
                        try:
                            child_type = child.element_info.control_type
                            if child_type == "MenuItem":
                                is_menu = True
                                break
                        except:
                            pass
            
            if is_menu:
                menu_found = True
                log(f"\n  [FOUND] Menu Window [{i}]: title='{win_title}', class='{win_class}'")
                
                try:
                    children = win.children()
                    log(f"    Has {len(children)} children")
                    
                    for j, child in enumerate(children):
                        try:
                            child_type = child.element_info.control_type
                            child_name = child.window_text()
                            log(f"      [{j}] {child_type}: '{child_name}'")
                            
                            if "Extensions" in child_name or "扩展" in child_name:
                                log(f"        [ALERT] Found Extensions menu item!")
                                extensions_item = child
                        except Exception as e:
                            log(f"      [{j}] Error: {e}")
                except Exception as e:
                    log(f"    Error getting children: {e}")
        except Exception as e:
            pass
    
    if not menu_found:
        log("  No menu windows found")
        
        log("\n  Checking all windows for MenuItem children...")
        for i, win in enumerate(all_windows):
            try:
                children = win.children()
                has_menu_items = False
                menu_items = []
                
                for child in children:
                    try:
                        child_type = child.element_info.control_type
                        if child_type == "MenuItem":
                            has_menu_items = True
                            child_name = child.window_text()
                            menu_items.append(child_name)
                    except:
                        pass
                
                if has_menu_items:
                    win_title = win.window_text()
                    log(f"\n  Window [{i}]: title='{win_title}'")
                    log(f"    Menu items: {', '.join(menu_items)}")
                    
                    for item_text in menu_items:
                        if "Extensions" in item_text or "扩展" in item_text:
                            log(f"      [ALERT] Found Extensions in menu!")
            except:
                pass
                
except Exception as e:
    log(f"[ERROR] Failed to send Alt+F: {e}")
    import traceback
    traceback.print_exc()

log("\n" + "="*60)
log("Debug Complete!")
log("="*60)
log(f"Output saved to: D:\\fund_helper\\autotest\\debug_output4.txt")
log("""
Summary:
1. We can start Edge and find its window via Desktop
2. We can connect to the process using the window's PID
3. We can find buttons in the window
4. We can try Alt+F and look for menu windows

Next Steps:
- Review the button list to find the Settings button
- Review the menu items to find Extensions
- Based on this, we can fix the windows_ui_controller.py
""")

log_file.close()

print("\nThe browser will remain open for 20 seconds...")
time.sleep(20)

try:
    app.kill()
    log("Browser closed")
except:
    pass
