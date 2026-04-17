import time
import subprocess
import os
import sys


class WindowsUIController:
    """
    使用 pywinauto 控制 Windows 原生 UI
    用于操作浏览器菜单、扩展图标等
    """
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.pywinauto_available = False
        
        try:
            from pywinauto import Application
            from pywinauto.keyboard import send_keys
            from pywinauto import mouse
            self.Application = Application
            self.send_keys = send_keys
            self.mouse = mouse
            self.pywinauto_available = True
            print("✓ pywinauto 已加载，可以操作 Windows 原生 UI")
        except ImportError as e:
            print(f"✗ pywinauto 未安装: {e}")
            print("  请运行: pip install pywinauto")
            self.pywinauto_available = False
    
    def is_available(self):
        return self.pywinauto_available
    
    def connect_to_edge(self, process_id=None):
        """
        连接到 Edge 浏览器窗口
        """
        if not self.pywinauto_available:
            return False
        
        try:
            print("\n正在连接到 Edge 浏览器...")
            
            if process_id:
                self.app = self.Application(backend='uia').connect(process=process_id)
            else:
                try:
                    self.app = self.Application(backend='uia').connect(
                        title_re=".*Microsoft Edge.*",
                        timeout=10
                    )
                except Exception:
                    self.app = self.Application(backend='uia').connect(
                        class_name="Chrome_WidgetWin_1",
                        timeout=10
                    )
            
            self.main_window = self.app.top_window()
            print(f"✓ 已连接到 Edge 浏览器: {self.main_window.window_text()}")
            return True
            
        except Exception as e:
            print(f"✗ 连接到 Edge 浏览器失败: {e}")
            return False
    
    def click_settings_button(self):
        """
        点击浏览器右上角的"设置及其他"按钮（三个点）
        步骤1: 点击三个点
        """
        if not self.pywinauto_available or not self.main_window:
            return False
        
        try:
            print("\n步骤1: 点击'设置及其他'按钮（三个点）...")
            
            settings_btn = None
            
            try:
                settings_btn = self.main_window.child_window(
                    title="设置及其他",
                    control_type="Button",
                    timeout=5
                )
            except Exception:
                pass
            
            if not settings_btn:
                try:
                    settings_btn = self.main_window.child_window(
                        title="Settings and more",
                        control_type="Button",
                        timeout=5
                    )
                except Exception:
                    pass
            
            if not settings_btn:
                try:
                    toolbar = self.main_window.child_window(
                        control_type="ToolBar",
                        timeout=5
                    )
                    buttons = toolbar.children(control_type="Button")
                    for btn in buttons:
                        try:
                            btn_title = btn.window_text()
                            if "设置" in btn_title or "Settings" in btn_title or "more" in btn_title.lower():
                                settings_btn = btn
                                break
                        except:
                            continue
                except Exception:
                    pass
            
            if settings_btn:
                settings_btn.click_input()
                print("✓ 已点击'设置及其他'按钮")
                time.sleep(1)
                return True
            else:
                print("  使用键盘快捷键 Alt+F...")
                self.send_keys('%{F}')
                time.sleep(1)
                return True
                
        except Exception as e:
            print(f"  点击'设置及其他'按钮失败: {e}")
            print("  尝试使用键盘快捷键 Alt+F...")
            self.send_keys('%{F}')
            time.sleep(1)
            return True
    
    def click_extensions_in_menu(self):
        """
        在菜单中点击"扩展"选项
        步骤2: 点击"扩展"
        """
        if not self.pywinauto_available:
            return False
        
        try:
            print("\n步骤2: 在菜单中点击'扩展'选项...")
            
            time.sleep(0.5)
            
            menu_window = None
            try:
                menu_windows = self.app.windows(
                    control_type="Menu",
                    timeout=2
                )
                if menu_windows:
                    menu_window = menu_windows[0]
            except Exception:
                pass
            
            if not menu_window:
                try:
                    popup_windows = self.app.windows(
                        control_type="Window",
                        timeout=2
                    )
                    for win in popup_windows:
                        try:
                            win_title = win.window_text()
                            if not win_title or "菜单" in win_title:
                                menu_window = win
                                break
                        except:
                            continue
                except Exception:
                    pass
            
            if menu_window:
                print(f"  找到菜单窗口: {menu_window.window_text()}")
                
                menu_items = menu_window.children(control_type="MenuItem")
                print(f"  找到 {len(menu_items)} 个菜单项")
                
                for item in menu_items:
                    try:
                        item_text = item.window_text()
                        print(f"    检查菜单项: '{item_text}'")
                        
                        if "扩展" in item_text or "Extensions" in item_text:
                            print(f"  ✓ 找到'扩展'选项: {item_text}")
                            item.click_input()
                            time.sleep(0.5)
                            return True
                    except Exception as e:
                        continue
                
                print("  未找到'扩展'选项，尝试使用键盘导航...")
                self.send_keys('{DOWN}')
                time.sleep(0.2)
                self.send_keys('{DOWN}')
                time.sleep(0.2)
                self.send_keys('{DOWN}')
                time.sleep(0.2)
                self.send_keys('{ENTER}')
                time.sleep(0.5)
                return True
            else:
                print("  未找到菜单窗口，尝试使用键盘导航...")
                self._navigate_menu_by_keyboard()
                return True
                
        except Exception as e:
            print(f"  点击'扩展'选项失败: {e}")
            print("  尝试使用键盘导航...")
            self._navigate_menu_by_keyboard()
            return True
    
    def _navigate_menu_by_keyboard(self):
        """
        使用键盘导航菜单找到"扩展"选项
        """
        print("\n  使用键盘导航菜单...")
        
        for i in range(15):
            try:
                print(f"    按向下键 {i+1}...")
                self.send_keys('{DOWN}')
                time.sleep(0.3)
                
                self.send_keys('{RIGHT}')
                time.sleep(0.3)
                
                self.send_keys('{ESC}')
                time.sleep(0.2)
                
            except Exception:
                continue
        
        print("  键盘导航完成")
    
    def click_extension_in_list(self, extension_name="自选基金助手"):
        """
        在扩展列表中点击目标扩展
        """
        if not self.pywinauto_available:
            return False
        
        try:
            print(f"\n在扩展列表中查找: {extension_name}...")
            
            time.sleep(1)
            
            popup_windows = self.app.windows(
                control_type="Window",
                timeout=2
            )
            
            for win in popup_windows:
                try:
                    win_title = win.window_text()
                    print(f"  检查窗口: {win_title}")
                    
                    list_items = win.children(control_type="ListItem")
                    print(f"  找到 {len(list_items)} 个列表项")
                    
                    for item in list_items:
                        try:
                            item_text = item.window_text()
                            print(f"    检查: '{item_text}'")
                            
                            if extension_name in item_text or "自选基金" in item_text:
                                print(f"  ✓ 找到扩展: {item_text}")
                                item.click_input()
                                time.sleep(0.5)
                                return True
                        except Exception:
                            continue
                except Exception:
                    continue
            
            print("  未找到扩展列表窗口")
            return False
            
        except Exception as e:
            print(f"  点击扩展失败: {e}")
            return False
    
    def click_extension_toolbar_icon(self):
        """
        点击工具栏中的扩展图标（拼图形状）
        """
        if not self.pywinauto_available or not self.main_window:
            return False
        
        try:
            print("\n点击工具栏中的扩展图标（拼图形状）...")
            
            extension_icon = None
            
            try:
                extension_icon = self.main_window.child_window(
                    title="扩展",
                    control_type="Button",
                    timeout=5
                )
            except Exception:
                pass
            
            if not extension_icon:
                try:
                    extension_icon = self.main_window.child_window(
                        title="Extensions",
                        control_type="Button",
                        timeout=5
                    )
                except Exception:
                    pass
            
            if not extension_icon:
                try:
                    toolbar = self.main_window.child_window(
                        control_type="ToolBar",
                        timeout=5
                    )
                    buttons = toolbar.children(control_type="Button")
                    for btn in buttons:
                        try:
                            btn_title = btn.window_text()
                            if "扩展" in btn_title or "Extensions" in btn_title:
                                extension_icon = btn
                                break
                        except:
                            continue
                except Exception:
                    pass
            
            if extension_icon:
                extension_icon.click_input()
                print("✓ 已点击扩展图标")
                time.sleep(1)
                return True
            else:
                print("  未找到扩展图标，尝试使用键盘快捷键...")
                return False
                
        except Exception as e:
            print(f"  点击扩展图标失败: {e}")
            return False
    
    def open_extension_full(self, extension_name="自选基金助手"):
        """
        完整的打开扩展流程：
        1. 点击三个点（设置及其他）
        2. 点击扩展
        3. 在扩展列表中点击目标扩展
        
        或者：
        1. 点击工具栏的扩展图标（拼图形状）
        2. 在弹出的列表中点击目标扩展
        """
        if not self.pywinauto_available:
            print("\n⚠️  pywinauto 不可用，无法自动化操作浏览器菜单")
            print("    请手动执行以下操作：")
            print("    1. 点击浏览器右上角的扩展图标（拼图形状）")
            print(f"    2. 在列表中点击'{extension_name}'")
            return False
        
        print("\n" + "="*60)
        print("使用 pywinauto 自动化打开扩展")
        print("="*60)
        
        print("\n方法1: 点击工具栏扩展图标（拼图形状）...")
        if self.click_extension_toolbar_icon():
            time.sleep(0.5)
            if self.click_extension_in_list(extension_name):
                print("\n✓ 扩展已打开！")
                return True
        
        print("\n方法2: 通过'设置及其他'菜单...")
        
        if not self.click_settings_button():
            print("  点击三个点失败")
            return False
        
        time.sleep(0.5)
        
        if not self.click_extensions_in_menu():
            print("  点击扩展失败")
            return False
        
        time.sleep(0.5)
        
        if self.click_extension_in_list(extension_name):
            print("\n✓ 扩展已打开！")
            return True
        
        print("\n⚠️  自动化操作可能已完成，请检查浏览器")
        print("    如果扩展未打开，请手动操作：")
        print("    1. 点击扩展图标")
        print(f"    2. 选择'{extension_name}'")
        
        return True
    
    def take_screenshot(self, filename):
        """
        使用 pywinauto 截图
        """
        if not self.pywinauto_available:
            return None
        
        try:
            from pywinauto import screenshot
            
            screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            
            filepath = os.path.join(screenshots_dir, filename)
            
            if self.main_window:
                self.main_window.capture_as_image().save(filepath)
            else:
                screenshot()
            
            print(f"  截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"  截图失败: {e}")
            return None
