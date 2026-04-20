import os
import sys
import time


class WindowsUIController:
    """
    Windows UI 控制器 - 用于操作浏览器的原生 UI
    
    ⚠️  重要说明：
    - pywinauto 在 Edge 浏览器的多进程架构下存在限制
    - Edge、飞书、Trae CN 等应用都使用相同的类名 Chrome_WidgetWin_1
    - 按钮没有明确的名称（如 "Settings" 或 "Extensions"）
    
    推荐方案：
    1. 使用 Playwright 启动浏览器和加载扩展（已可靠实现）
    2. 对于扩展弹窗的打开，提供清晰的手动操作指南
    3. 脚本会等待用户操作并检测扩展弹窗
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
            print("[OK] pywinauto 已加载")
        except ImportError as e:
            print(f"[WARNING] pywinauto 未安装: {e}")
            print("  请运行: pip install pywinauto")
            self.pywinauto_available = False
    
    def is_available(self):
        return self.pywinauto_available
    
    def print_manual_instructions(self):
        """
        打印手动操作指南
        """
        print("\n" + "="*60)
        print("📋 手动操作指南")
        print("="*60)
        print("""
由于浏览器安全限制，无法完全自动化以下操作。
请手动执行以下步骤：

┌─────────────────────────────────────────────────────────────┐
│  方法1: 点击扩展图标（推荐）                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  步骤1: 找到浏览器工具栏中的扩展图标                          │
│         位置：地址栏右侧，收藏夹图标旁边                      │
│         图标：拼图形状                                        │
│                                                              │
│  步骤2: 点击扩展图标                                          │
│         将弹出已安装的扩展列表                                │
│                                                              │
│  步骤3: 在列表中找到并点击：                                  │
│         "自选基金助手 - 实时查看基金涨跌幅 2.5.2"            │
│                                                              │
│  步骤4: 扩展弹窗将打开，测试将自动继续执行                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  方法2: 通过三点菜单（备选）                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  步骤1: 点击浏览器右上角的三个点（设置及其他）                │
│         位置：浏览器最右上角                                  │
│                                                              │
│  步骤2: 在弹出的菜单中找到"扩展"选项                         │
│         注意："扩展"旁边有箭头，表示有子菜单                  │
│                                                              │
│  步骤3: 将鼠标悬停在"扩展"上，将显示子菜单                    │
│                                                              │
│  步骤4: 在子菜单中点击：                                      │
│         "自选基金助手 - 实时查看基金涨跌幅 2.5.2"            │
│         或者点击"管理扩展"查看所有扩展                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘

⏳ 脚本将等待最多 120 秒，检测扩展弹窗是否打开。
   检测到后，测试将自动继续执行。

💡 提示：
- 如果扩展列表中没有显示，请点击"管理扩展"
- 在扩展管理页面确保"自选基金助手"开关已打开（蓝色）
- 如果扩展未显示，请检查是否已正确加载

""")
        print("="*60)
    
    def try_open_extension_with_keyboard(self):
        """
        尝试使用键盘快捷键打开菜单
        注意：这是备选方案，可能不完全可靠
        """
        if not self.pywinauto_available:
            return False
        
        print("\n[尝试] 使用键盘快捷键打开菜单...")
        print("  注意：这是备选方案，可能不完全可靠")
        
        try:
            print("  发送 Alt+F 快捷键...")
            self.send_keys('%{F}')
            time.sleep(1)
            print("  [OK] 已发送 Alt+F")
            
            print("  尝试导航到'扩展'选项...")
            print("  注意：需要知道'扩展'在菜单中的位置")
            
            for i in range(10):
                self.send_keys('{DOWN}')
                time.sleep(0.2)
            
            print("  [OK] 已导航")
            print("  提示：如果菜单未正确打开，请使用手动操作")
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] 键盘操作失败: {e}")
            return False
    
    def connect_to_browser(self, process_id=None):
        """
        尝试连接到浏览器
        注意：由于 Edge 的多进程架构，这可能不完全可靠
        """
        if not self.pywinauto_available:
            return False
        
        print("\n[尝试] 连接到 Edge 浏览器...")
        print("  注意：由于 Edge 的多进程架构，这可能不完全可靠")
        
        try:
            if process_id:
                print(f"  尝试连接到进程 ID: {process_id}")
                self.app = self.Application(backend='uia').connect(process=process_id)
            else:
                print("  尝试通过标题连接...")
                try:
                    self.app = self.Application(backend='uia').connect(
                        title_re=".*Edge.*",
                        timeout=10
                    )
                except Exception:
                    print("  尝试通过类名连接...")
                    self.app = self.Application(backend='uia').connect(
                        class_name="Chrome_WidgetWin_1",
                        timeout=10
                    )
            
            self.main_window = self.app.top_window()
            print(f"  [OK] 已连接到窗口: {self.main_window.window_text()}")
            return True
            
        except Exception as e:
            print(f"  [ERROR] 连接失败: {e}")
            print("  原因：Edge 使用多进程架构，多个应用使用相同类名")
            print("  建议：使用手动操作")
            return False
    
    def click_settings_button(self):
        """
        尝试点击设置按钮（三个点）
        注意：Edge 的按钮没有明确名称，这可能不可靠
        """
        if not self.pywinauto_available or not self.main_window:
            return False
        
        print("\n[尝试] 点击设置按钮...")
        print("  注意：Edge 的按钮没有明确名称，这可能不可靠")
        
        try:
            all_buttons = self.main_window.descendants(control_type="Button")
            print(f"  找到 {len(all_buttons)} 个按钮")
            
            for btn in all_buttons:
                try:
                    btn_name = btn.window_text()
                    btn_automation_id = ""
                    try:
                        btn_automation_id = btn.element_info.automation_id
                    except:
                        pass
                    
                    if "Settings" in btn_name or "more" in btn_name.lower() or "more" in btn_automation_id.lower():
                        print(f"  [找到] 可能的设置按钮: name='{btn_name}', automation_id='{btn_automation_id}'")
                        btn.click_input()
                        time.sleep(1)
                        print("  [OK] 已点击")
                        return True
                except:
                    continue
            
            print("  [WARNING] 未找到明确的设置按钮")
            print("  建议：使用手动操作")
            return False
            
        except Exception as e:
            print(f"  [ERROR] 查找按钮失败: {e}")
            return False
    
    def click_extensions_button(self):
        """
        尝试点击扩展按钮
        注意：Edge 的按钮没有明确名称，这可能不可靠
        """
        if not self.pywinauto_available or not self.main_window:
            return False
        
        print("\n[尝试] 点击扩展按钮...")
        print("  注意：Edge 的按钮没有明确名称，这可能不可靠")
        
        try:
            all_buttons = self.main_window.descendants(control_type="Button")
            
            for btn in all_buttons:
                try:
                    btn_name = btn.window_text()
                    btn_automation_id = ""
                    try:
                        btn_automation_id = btn.element_info.automation_id
                    except:
                        pass
                    
                    if "Extensions" in btn_name or "extension" in btn_automation_id.lower():
                        print(f"  [找到] 可能的扩展按钮: name='{btn_name}', automation_id='{btn_automation_id}'")
                        btn.click_input()
                        time.sleep(1)
                        print("  [OK] 已点击")
                        return True
                except:
                    continue
            
            print("  [WARNING] 未找到明确的扩展按钮")
            print("  建议：使用手动操作")
            return False
            
        except Exception as e:
            print(f"  [ERROR] 查找按钮失败: {e}")
            return False
    
    def open_extension_automated(self, extension_name="自选基金助手"):
        """
        尝试自动化打开扩展
        注意：由于 Edge 的限制，这可能不完全可靠
        建议使用手动操作
        """
        print("\n" + "="*60)
        print("🔧 尝试自动化打开扩展")
        print("="*60)
        print("""
⚠️  重要提示：
由于以下原因，自动化可能不完全可靠：
1. Edge 浏览器使用多进程架构
2. 多个应用使用相同的类名 (Chrome_WidgetWin_1)
3. 按钮没有明确的名称（如 "Settings" 或 "Extensions"）

如果自动化失败，请使用手动操作。
""")
        
        if not self.pywinauto_available:
            print("\n[ERROR] pywinauto 不可用")
            self.print_manual_instructions()
            return False
        
        if not self.main_window:
            print("\n[ERROR] 未连接到浏览器窗口")
            self.print_manual_instructions()
            return False
        
        print("\n[方法1] 尝试点击工具栏扩展图标...")
        if self.click_extensions_button():
            print("  [OK] 扩展图标已点击")
            print("  请在弹出的列表中选择目标扩展")
            print("  脚本将等待扩展弹窗打开...")
            return True
        
        print("\n[方法2] 尝试点击设置按钮...")
        if self.click_settings_button():
            print("  [OK] 设置按钮已点击")
            print("  请在菜单中导航到'扩展'选项")
            print("  脚本将等待扩展弹窗打开...")
            return True
        
        print("\n[方法3] 尝试使用键盘快捷键...")
        if self.try_open_extension_with_keyboard():
            print("  [OK] 键盘快捷键已发送")
            print("  请在菜单中导航到'扩展'选项")
            print("  脚本将等待扩展弹窗打开...")
            return True
        
        print("\n" + "!"*60)
        print("⚠️  所有自动化方法都失败了")
        print("!"*60)
        self.print_manual_instructions()
        
        return False
