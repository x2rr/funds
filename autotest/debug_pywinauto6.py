# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess

log_file = open(r"D:\fund_helper\autotest\debug_output5.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()

log("="*60)
log("pywinauto Debug Script - Use Window Directly")
log("="*60)

log("\nStep 1: Check if pywinauto is installed...")
try:
    from pywinauto import Application
    from pywinauto.keyboard import send_keys
    from pywinauto import Desktop
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

log("\nStep 3: List Edge windows before starting new one...")
desktop = Desktop(backend="uia")

edge_windows_before = []
try:
    all_windows = desktop.windows()
    log(f"  Found {len(all_windows)} windows on desktop")
    
    for i, win in enumerate(all_windows):
        try:
            win_title = win.window_text()
            win_class = win.element_info.class_name
            
            if "Chrome_WidgetWin" in win_class:
                log(f"    Chrome_WidgetWin [{i}]: title='{win_title}', class='{win_class}'")
                edge_windows_before.append(win)
        except:
            pass
    
    log(f"  Found {len(edge_windows_before)} Chrome_WidgetWin windows before")
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
                    win_class = win.element_info.class_name
                    if "Chrome_WidgetWin" in win_class:
                        edge_windows_now.append(win)
                except:
                    pass
            
            log(f"    Attempt {attempt + 1}: Found {len(edge_windows_now)} Chrome_WidgetWin windows")
            
            if len(edge_windows_now) > len(edge_windows_before):
                log("      New window detected!")
                
                for win in edge_windows_now:
                    is_new = True
                    
                    for old_win in edge_windows_before:
                        try:
                            if win.element_info.handle == old_win.element_info.handle:
                                is_new = False
                                break
                        except:
                            pass
                    
                    if is_new:
                        new_edge_window = win
                        try:
                            win_title = win.window_text()
                            win_class = win.element_info.class_name
                            log(f"      [FOUND] New window: title='{win_title}', class='{win_class}'")
                        except:
                            log(f"      [FOUND] New window (could not get title)")
                        break
                
                if new_edge_window:
                    break
        except Exception as e:
            log(f"    Error: {e}")
    
    if new_edge_window is None:
        log("\n  Could not find new window by handle difference")
        log("  Taking the last Chrome_WidgetWin window...")
        
        all_windows = desktop.windows()
        for i, win in enumerate(all_windows):
            try:
                win_class = win.element_info.class_name
                if "Chrome_WidgetWin" in win_class:
                    new_edge_window = win
                    try:
                        win_title = win.window_text()
                        log(f"    Selected [{i}]: title='{win_title}', class='{win_class}'")
                    except:
                        log(f"    Selected [{i}]: class='{win_class}'")
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

log("\nStep 5: Work with the window directly (no app.connect)...")
main_window = new_edge_window

log("\nStep 6: Set focus to window...")
try:
    main_window.set_focus()
    log("[OK] Focus set")
    time.sleep(1)
except Exception as e:
    log(f"[WARNING] Failed to set focus: {e}")

log("\nStep 7: Print window info...")
try:
    win_title = main_window.window_text()
    win_class = main_window.element_info.class_name
    win_handle = main_window.element_info.handle
    win_pid = main_window.element_info.process_id
    
    log(f"  Title: '{win_title}'")
    log(f"  Class: '{win_class}'")
    log(f"  Handle: {win_handle}")
    log(f"  PID: {win_pid}")
except Exception as e:
    log(f"  [ERROR] Failed to get window info: {e}")

log("\nStep 8: Print all descendants (first 100)...")
try:
    all_descendants = main_window.descendants()
    log(f"  Found {len(all_descendants)} descendants")
    
    log("\n  Listing first 100 descendants:")
    for i, desc in enumerate(all_descendants[:100]):
        try:
            desc_type = desc.element_info.control_type
            desc_name = desc.window_text()
            desc_class = ""
            try:
                desc_class = desc.element_info.class_name
            except:
                pass
            
            log(f"    [{i}] {desc_type}: name='{desc_name}', class='{desc_class}'")
            
            if "Button" in desc_type:
                log(f"        [ALERT] This is a Button!")
            
            if "Settings" in desc_name or "more" in desc_name.lower():
                log(f"        [ALERT] May be Settings button!")
            
            if "Extensions" in desc_name:
                log(f"        [ALERT] May be Extensions button!")
        except Exception as e:
            log(f"    [{i}] Error: {e}")
except Exception as e:
    log(f"  [ERROR] Failed to get descendants: {e}")

log("\nStep 9: Find all Button controls...")
try:
    all_buttons = main_window.descendants(control_type="Button")
    log(f"  Found {len(all_buttons)} Button controls")
    
    settings_button = None
    extensions_button = None
    
    log("\n  Listing all buttons:")
    for i, btn in enumerate(all_buttons):
        try:
            btn_name = btn.window_text()
            btn_automation_id = ""
            try:
                btn_automation_id = btn.element_info.automation_id
            except:
                pass
            
            log(f"    [{i}] Button: name='{btn_name}', automation_id='{btn_automation_id}'")
            
            if "Settings" in btn_name or "more" in btn_name.lower() or "more" in btn_automation_id.lower():
                log(f"        [ALERT] This may be the Settings button!")
                settings_button = btn
            
            if "Extensions" in btn_name or "extension" in btn_automation_id.lower():
                log(f"        [ALERT] This may be the Extensions icon!")
                extensions_button = btn
                
        except Exception as e:
            log(f"    [{i}] Error: {e}")
except Exception as e:
    log(f"  [ERROR] Failed to find buttons: {e}")

log("\nStep 10: Try to click Settings button if found...")
if settings_button:
    try:
        log("  Clicking Settings button...")
        settings_button.click_input()
        log("  [OK] Settings button clicked")
        time.sleep(2)
    except Exception as e:
        log(f"  [ERROR] Failed to click Settings button: {e}")
else:
    log("  Settings button not found, trying Alt+F instead...")
    try:
        log("  Setting focus to window...")
        main_window.set_focus()
        time.sleep(0.5)
        
        log("  Sending Alt+F...")
        send_keys('%{F}')
        log("  [OK] Alt+F sent")
        time.sleep(2)
    except Exception as e:
        log(f"  [ERROR] Failed to send Alt+F: {e}")

log("\nStep 11: Check for menu windows...")
try:
    log("  Checking all windows from Desktop...")
    all_windows = desktop.windows()
    log(f"  Found {len(all_windows)} windows on desktop")
    
    menu_found = False
    extensions_menu_item = None
    
    for i, win in enumerate(all_windows):
        try:
            win_title = win.window_text()
            win_class = win.element_info.class_name
            
            is_menu = False
            if "Menu" in win_title or "menu" in win_title.lower():
                is_menu = True
            
            if not win_title:
                try:
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
                                extensions_menu_item = child
                        except Exception as e:
                            log(f"      [{j}] Error: {e}")
                except Exception as e:
                    log(f"    Error getting children: {e}")
        except Exception as e:
            pass
    
    if not menu_found:
        log("  No menu windows found with obvious titles")
        
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
    log(f"[ERROR] Failed to check menu windows: {e}")
    import traceback
    traceback.print_exc()

log("\nStep 12: Try to click Extensions menu item if found...")
if extensions_menu_item:
    try:
        log("  Clicking Extensions menu item...")
        extensions_menu_item.click_input()
        log("  [OK] Extensions menu item clicked")
        time.sleep(2)
        
        log("\n  Checking for submenu...")
        all_windows = desktop.windows()
        
        for i, win in enumerate(all_windows):
            try:
                children = win.children()
                
                for j, child in enumerate(children):
                    try:
                        child_type = child.element_info.control_type
                        child_name = child.window_text()
                        if child_type == "MenuItem":
                            log(f"    Submenu item: '{child_name}'")
                            
                            if "Manage" in child_name or "管理" in child_name:
                                log(f"      [ALERT] Found Manage extensions!")
                                child.click_input()
                                log("      [OK] Clicked Manage extensions")
                    except:
                        pass
            except:
                pass
                
    except Exception as e:
        log(f"  [ERROR] Failed to click Extensions menu: {e}")

log("\n" + "="*60)
log("Debug Complete!")
log("="*60)
log(f"Output saved to: D:\\fund_helper\\autotest\\debug_output5.txt")
log("""
Key Findings:
1. We can find the new Edge window
2. We need to check what buttons are available
3. We need to see what menu items appear after Alt+F

Please review the debug output carefully to understand:
- What buttons exist in the window
- What menu items appear when Alt+F is pressed
- How to interact with the Extensions menu
""")

log_file.close()

print("\nThe browser will remain open for 20 seconds...")
time.sleep(20)

try:
    log("Closing browser...")
    main_window.close()
except:
    pass
