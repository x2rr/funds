# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess

log_file = open(r"D:\fund_helper\autotest\debug_output3.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()

log("="*60)
log("pywinauto Debug Script - Using Application.start()")
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

log("\nStep 3: Start Edge using pywinauto Application.start()...")
try:
    log(f"  Starting: {edge_executable} about:blank")
    app = Application(backend='uia').start(
        f'"{edge_executable}" about:blank --new-window'
    )
    log("[OK] Edge started via pywinauto")
    
    log("\n  Waiting for browser to initialize...")
    time.sleep(5)
    
except Exception as e:
    log(f"[ERROR] Failed to start Edge: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

log("\nStep 4: Get main window...")
main_window = None
try:
    windows = app.windows()
    log(f"  Found {len(windows)} windows in the app")
    
    for i, win in enumerate(windows):
        try:
            win_title = win.window_text()
            win_class = win.element_info.class_name
            win_visible = win.is_visible()
            log(f"    Window [{i}]: title='{win_title}', class='{win_class}', visible={win_visible}")
            
            if win_visible:
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

log("\nStep 5: Set focus to main window...")
try:
    main_window.set_focus()
    log("[OK] Focus set to main window")
    time.sleep(1)
except Exception as e:
    log(f"[WARNING] Failed to set focus: {e}")

log("\nStep 6: Find all buttons in main window...")
try:
    all_buttons = main_window.descendants(control_type="Button")
    log(f"Found {len(all_buttons)} buttons")
    
    log("\nListing all buttons (first 60):")
    settings_button = None
    extensions_button = None
    
    for i, btn in enumerate(all_buttons[:60]):
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

log("\nStep 7: Try clicking the Settings button if found...")
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
        log("  Sending Alt+F...")
        main_window.set_focus()
        time.sleep(0.5)
        send_keys('%{F}')
        log("  [OK] Alt+F sent")
        time.sleep(2)
    except Exception as e:
        log(f"  [ERROR] Failed to send Alt+F: {e}")

log("\nStep 8: Check for menu windows...")
try:
    log("  Checking all windows from Desktop...")
    desktop = Desktop(backend="uia")
    
    all_windows = desktop.windows()
    log(f"  Found {len(all_windows)} windows on desktop")
    
    menu_found = False
    extensions_menu_item = None
    
    for i, win in enumerate(all_windows):
        try:
            win_title = win.window_text()
            win_class = win.element_info.class_name
            
            if "Menu" in win_title or "menu" in win_title.lower() or not win_title:
                log(f"\n  Potential Menu [{i}]: title='{win_title}', class='{win_class}'")
                menu_found = True
                
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
        
        log("\n  Checking all windows more thoroughly...")
        for i, win in enumerate(all_windows):
            try:
                win_title = win.window_text()
                children = win.children()
                if len(children) > 0:
                    has_menu_items = False
                    menu_items_text = []
                    
                    for child in children:
                        try:
                            child_type = child.element_info.control_type
                            if child_type == "MenuItem":
                                has_menu_items = True
                                child_name = child.window_text()
                                menu_items_text.append(child_name)
                        except:
                            pass
                    
                    if has_menu_items:
                        log(f"\n  Window [{i}]: title='{win_title}'")
                        log(f"    Menu items: {', '.join(menu_items_text)}")
                        
                        for item_text in menu_items_text:
                            if "Extensions" in item_text or "扩展" in item_text:
                                log(f"      [ALERT] Found Extensions in menu!")
            except:
                pass
                
except Exception as e:
    log(f"[ERROR] Failed to check menu windows: {e}")
    import traceback
    traceback.print_exc()

log("\nStep 9: Try to click Extensions menu item if found...")
if extensions_menu_item:
    try:
        log("  Clicking Extensions menu item...")
        extensions_menu_item.click_input()
        log("  [OK] Extensions menu item clicked")
        time.sleep(2)
        
        log("\n  Checking for submenu...")
        desktop = Desktop(backend="uia")
        all_windows = desktop.windows()
        
        for i, win in enumerate(all_windows):
            try:
                win_title = win.window_text()
                children = win.children()
                
                for j, child in enumerate(children):
                    try:
                        child_type = child.element_info.control_type
                        child_name = child.window_text()
                        if child_type == "MenuItem":
                            log(f"    Submenu item: '{child_name}'")
                            
                            if "Manage" in child_name or "管理" in child_name or "扩展" in child_name:
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
log(f"Output saved to: D:\\fund_helper\\autotest\\debug_output3.txt")
log("""
Key Findings Summary:
1. Check the buttons list for Settings and Extensions buttons
2. Check what menu items appear when Alt+F is pressed
3. Look for "Extensions" in the menu items
""")

log_file.close()

print("\nThe browser will remain open for 30 seconds for manual inspection...")
print("You can manually test:")
print("  1. Click the three dots (Settings and more)")
print("  2. Hover over 'Extensions' to see the submenu")
print("  3. Click 'Manage extensions'")

time.sleep(30)

try:
    app.kill()
    log("Browser closed")
except:
    pass
