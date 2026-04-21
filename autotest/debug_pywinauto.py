# -*- coding: utf-8 -*-
import os
import sys
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("="*60)
print("pywinauto Debug Script")
print("="*60)

print("\nStep 1: Check if pywinauto is installed...")
try:
    from pywinauto import Application
    from pywinauto.keyboard import send_keys
    from pywinauto import mouse
    print("[OK] pywinauto is installed")
except ImportError as e:
    print(f"[ERROR] pywinauto not installed: {e}")
    print("   Please run: pip install pywinauto")
    sys.exit(1)

print("\nStep 2: Find Edge browser path...")
edge_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"),
    os.path.expandvars(r"%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe"),
]

edge_executable = None
for path in edge_paths:
    if os.path.exists(path):
        edge_executable = path
        break

if edge_executable:
    print(f"[OK] Found Edge: {edge_executable}")
else:
    print("[ERROR] Edge browser not found")
    sys.exit(1)

print("\nStep 3: Start Edge browser...")
try:
    app = Application(backend='uia').start(edge_executable)
    print("[OK] Edge browser started")
    time.sleep(3)
except Exception as e:
    print(f"[ERROR] Failed to start Edge: {e}")
    sys.exit(1)

print("\nStep 4: Connect to Edge window...")
try:
    app = Application(backend='uia').connect(
        title_re=".*Microsoft Edge.*",
        timeout=10
    )
    print("[OK] Connected to Edge browser")
except Exception as e:
    print(f"[ERROR] Failed to connect: {e}")
    
    print("\nTrying to connect by class_name...")
    try:
        app = Application(backend='uia').connect(
            class_name="Chrome_WidgetWin_1",
            timeout=5
        )
        print("[OK] Connected by class_name")
    except Exception as e2:
        print(f"[ERROR] Still failed: {e2}")
        sys.exit(1)

print("\nStep 5: Get main window...")
try:
    main_window = app.top_window()
    print(f"[OK] Main window title: {main_window.window_text()}")
except Exception as e:
    print(f"[ERROR] Failed to get main window: {e}")
    sys.exit(1)

print("\nStep 6: Print window control tree (first 20 controls)...")
try:
    print("="*60)
    print("Control Tree:")
    print("="*60)
    
    children = main_window.children()
    print(f"Found {len(children)} direct children")
    
    for i, child in enumerate(children[:20]):
        try:
            ctrl_type = child.element_info.control_type
            ctrl_name = child.window_text()
            print(f"  [{i}] {ctrl_type}: '{ctrl_name}'")
        except Exception as e:
            print(f"  [{i}] (Cannot get control info)")
except Exception as e:
    print(f"[ERROR] Failed to print control tree: {e}")

print("\nStep 7: Find ToolBar...")
try:
    toolbars = main_window.children(control_type="ToolBar")
    print(f"Found {len(toolbars)} toolbars")
    
    for i, toolbar in enumerate(toolbars):
        try:
            toolbar_name = toolbar.window_text()
            print(f"  ToolBar [{i}]: '{toolbar_name}'")
            
            toolbar_children = toolbar.children()
            print(f"    Contains {len(toolbar_children)} children")
            
            for j, child in enumerate(toolbar_children[:15]):
                try:
                    ctrl_type = child.element_info.control_type
                    ctrl_name = child.window_text()
                    print(f"      [{j}] {ctrl_type}: '{ctrl_name}'")
                    
                    if "Settings" in ctrl_name or "more" in ctrl_name.lower():
                        print(f"      [ALERT] May be Settings button!")
                    
                    if "Extensions" in ctrl_name:
                        print(f"      [ALERT] May be Extensions icon!")
                        
                except Exception:
                    continue
        except Exception:
            continue
except Exception as e:
    print(f"[ERROR] Failed to find toolbar: {e}")

print("\nStep 8: Find all buttons...")
try:
    all_buttons = main_window.descendants(control_type="Button")
    print(f"Found {len(all_buttons)} buttons")
    
    print("\nLooking for 'Settings' or 'Extensions' buttons:")
    for i, btn in enumerate(all_buttons[:50]):
        try:
            btn_name = btn.window_text()
            if btn_name:
                print(f"  [{i}] Button: '{btn_name}'")
                
                if "Settings" in btn_name or "more" in btn_name.lower():
                    print(f"      [ALERT] May be Settings button!")
                
                if "Extensions" in btn_name:
                    print(f"      [ALERT] May be Extensions icon!")
        except Exception:
            continue
except Exception as e:
    print(f"[ERROR] Failed to find buttons: {e}")

print("\nStep 9: Try keyboard shortcut Alt+F to open menu...")
try:
    print("   Pressing Alt+F...")
    send_keys('%{F}')
    time.sleep(2)
    print("[OK] Alt+F sent")
    
    print("\nStep 10: Check if menu window is open...")
    try:
        menu_windows = app.windows(control_type="Menu")
        print(f"Found {len(menu_windows)} menu windows")
        
        for i, menu in enumerate(menu_windows):
            try:
                menu_name = menu.window_text()
                print(f"  Menu [{i}]: '{menu_name}'")
                
                menu_items = menu.children(control_type="MenuItem")
                print(f"    Contains {len(menu_items)} menu items")
                
                for j, item in enumerate(menu_items):
                    try:
                        item_name = item.window_text()
                        print(f"      [{j}] MenuItem: '{item_name}'")
                        
                        if "Extensions" in item_name:
                            print(f"        [ALERT] Found 'Extensions' menu item!")
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception as e:
        print(f"[ERROR] Failed to find menu windows: {e}")
        
except Exception as e:
    print(f"[ERROR] Failed to send shortcut: {e}")

print("\n" + "="*60)
print("Debug Complete!")
print("="*60)
print("""
Next Steps:
1. Review the output above to find:
   - Buttons containing "Settings" or "more" (Settings and more button)
   - Buttons containing "Extensions" (Extensions icon)

2. Check if "Extensions" option exists in the menu opened by Alt+F

3. Modify windows_ui_controller.py based on the debug results
""")

print("\nThe browser window will remain open for 30 seconds...")
print("You can manually test:")
print("  1. Click the three dots (Settings and more)")
print("  2. Hover over 'Extensions' to see the submenu")
print("  3. Click 'Manage extensions' to see the extensions page")

time.sleep(30)

try:
    app.kill()
    print("Browser closed")
except:
    pass
