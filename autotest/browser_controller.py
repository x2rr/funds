import os
import asyncio
import time
from config import (
    EDGE_EXTENSIONS_URL,
    EXTENSION_PATH,
    EXTENSION_NAME,
)


class BrowserController:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.extension_id = None
        self.windows_ui = None
        self.browser_process_id = None
        
        try:
            from windows_ui_controller import WindowsUIController
            self.windows_ui = WindowsUIController()
        except ImportError as e:
            print(f"警告: 无法加载 Windows UI 控制器: {e}")
            self.windows_ui = None
    
    async def start(self):
        try:
            from playwright.async_api import async_playwright
            
            print("正在启动浏览器...")
            self.playwright = await async_playwright().start()
            
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
            
            if not edge_executable:
                print("警告: 未找到 Edge 浏览器，尝试使用系统默认...")
                edge_executable = "msedge"
            
            print(f"使用 Edge 浏览器: {edge_executable}")
            
            args = [
                f"--disable-extensions-except={EXTENSION_PATH}",
                f"--load-extension={EXTENSION_PATH}",
            ]
            
            if self.headless:
                args.append("--headless=new")
            
            print(f"\n启动参数:")
            print(f"  --disable-extensions-except={EXTENSION_PATH}")
            print(f"  --load-extension={EXTENSION_PATH}")
            print("\n✅ 扩展已通过启动参数预加载，无需手动加载！")
            print("   这等效于:")
            print("     1. 打开 edge://extensions/")
            print("     2. 开启开发者模式")
            print("     3. 点击'加载解压的扩展'")
            print("     4. 选择扩展目录")
            
            self.browser = await self.playwright.chromium.launch(
                executable_path=edge_executable,
                headless=self.headless,
                args=args,
            )
            
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            
            self.page = await self.context.new_page()
            
            if self.windows_ui and self.windows_ui.is_available():
                print("\n正在连接 Windows UI 控制器...")
                await asyncio.sleep(1)
                
                if self.windows_ui.connect_to_edge():
                    print("✅ Windows UI 控制器已连接")
                else:
                    print("⚠️  Windows UI 控制器连接失败，将使用备用方案")
            
            print("\n✅ 浏览器启动成功!")
            return True
            
        except Exception as e:
            print(f"启动浏览器失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def close(self):
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("浏览器已关闭")
        except Exception as e:
            print(f"关闭浏览器时出错: {e}")
    
    async def navigate_to_extensions(self):
        try:
            print(f"正在导航到扩展管理页面: {EDGE_EXTENSIONS_URL}")
            await self.page.goto(EDGE_EXTENSIONS_URL, wait_until="networkidle")
            await asyncio.sleep(2)
            print("已进入扩展管理页面")
            return True
        except Exception as e:
            print(f"导航到扩展管理页面失败: {e}")
            return False
    
    async def enable_developer_mode(self):
        try:
            print("正在检查并启用开发者模式...")
            
            developer_toggle = await self.page.query_selector('[aria-label*="开发人员模式"]')
            if not developer_toggle:
                developer_toggle = await self.page.query_selector('input[type="checkbox"]')
            
            if developer_toggle:
                is_checked = await developer_toggle.is_checked()
                if not is_checked:
                    await developer_toggle.click()
                    await asyncio.sleep(1)
                    print("开发者模式已启用")
                else:
                    print("开发者模式已处于启用状态")
            else:
                print("警告: 未找到开发者模式开关")
            
            return True
        except Exception as e:
            print(f"启用开发者模式失败: {e}")
            return False
    
    async def check_extension_loaded(self):
        try:
            print("检查扩展是否已加载...")
            
            await self.page.goto(EDGE_EXTENSIONS_URL, wait_until="networkidle")
            await asyncio.sleep(2)
            
            extension_cards = await self.page.query_selector_all('[role="listitem"]')
            
            for card in extension_cards:
                try:
                    text = await card.inner_text()
                    if EXTENSION_NAME in text or "自选基金助手" in text:
                        print(f"✅ 扩展已加载: {EXTENSION_NAME}")
                        return True
                except:
                    continue
            
            print("警告: 未在扩展列表中找到目标扩展")
            return False
            
        except Exception as e:
            print(f"检查扩展加载状态失败: {e}")
            return False
    
    async def open_extension_via_menu(self):
        """
        使用 pywinauto 自动化打开扩展：
        方法1: 点击工具栏扩展图标（拼图形状）→ 选择目标扩展
        方法2: 点击三个点（设置及其他）→ 扩展 → 选择目标扩展
        """
        print("\n" + "="*60)
        print("步骤3: 打开扩展并准备测试")
        print("="*60)
        
        if self.windows_ui and self.windows_ui.is_available():
            print("\n✅ 使用 pywinauto 自动化操作浏览器菜单...")
            print("""
操作流程：
┌─────────────────────────────────────────────────────────────┐
│  方法1（推荐）:                                              │
│  1. 点击工具栏中的扩展图标（拼图形状）                        │
│  2. 在弹出的列表中点击"自选基金助手"                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  方法2（备选）:                                              │
│  1. 点击右上角的三个点（设置及其他）                          │
│  2. 在菜单中点击"扩展"                                        │
│  3. 在扩展列表中点击"自选基金助手"                            │
└─────────────────────────────────────────────────────────────┘
""")
            
            success = self.windows_ui.open_extension_full(EXTENSION_NAME)
            
            if success:
                print("\n✅ pywinauto 自动化操作已执行")
                print("   正在检测扩展弹窗是否打开...")
                
                for i in range(10):
                    pages = self.context.pages
                    for page in pages:
                        try:
                            url = page.url
                            if ("popup.html" in url.lower() or 
                                (url.startswith("chrome-extension://") and 
                                 ("popup" in url.lower() or "fund" in url.lower() or "choose" in url.lower()))):
                                print(f"\n✅ 检测到扩展弹窗: {url}")
                                self.page = page
                                await self.take_screenshot("extension_popup_opened.png")
                                return True
                        except:
                            continue
                    
                    await asyncio.sleep(1)
                
                print("\n⚠️  未检测到独立的扩展弹窗页面")
                print("   可能的原因：")
                print("   1. 扩展弹窗可能在当前页面中显示")
                print("   2. pywinauto 操作可能需要手动确认")
                print("\n如果扩展未打开，请手动执行：")
                print("   1. 点击扩展图标（拼图形状）")
                print("   2. 选择'自选基金助手'")
                
                return self._wait_for_manual_operation()
            else:
                print("\n⚠️  pywinauto 自动化操作可能未完全成功")
                return self._wait_for_manual_operation()
        else:
            print("\n⚠️  pywinauto 不可用")
            print("   请安装: pip install pywinauto")
            return self._wait_for_manual_operation()
    
    async def _wait_for_manual_operation(self):
        """等待用户手动操作打开扩展"""
        print("\n" + "!"*60)
        print("需要手动操作")
        print("!"*60)
        print("""
请手动执行以下操作：
┌─────────────────────────────────────────────────────────────┐
│  操作步骤：                                                   │
│                                                              │
│  1. 找到浏览器工具栏中的扩展图标（拼图形状）                  │
│     位置：地址栏右侧，收藏夹图标旁边                          │
│                                                              │
│  2. 点击扩展图标，将弹出已安装的扩展列表                      │
│                                                              │
│  3. 在列表中找到并点击：                                      │
│     "自选基金助手 - 实时查看基金涨跌幅 2.5.2"                │
│                                                              │
│  4. 扩展弹窗将打开，测试将自动继续执行                        │
└─────────────────────────────────────────────────────────────┘

如果扩展列表中没有显示：
- 点击"管理扩展"
- 在扩展管理页面找到"自选基金助手"
- 确保扩展开关已打开（蓝色）
""")
        
        print("\n⏳ 等待手动操作 (最多等待 120 秒)...")
        
        for i in range(120):
            pages = self.context.pages
            for page in pages:
                try:
                    url = page.url
                    if ("popup.html" in url.lower() or 
                        (url.startswith("chrome-extension://") and 
                         ("popup" in url.lower() or "fund" in url.lower() or "choose" in url.lower()))):
                        print(f"\n✅ 检测到扩展弹窗: {url}")
                        self.page = page
                        await self.take_screenshot("extension_popup_opened.png")
                        print("\n✅ 扩展弹窗已打开，继续执行测试...")
                        return True
                except:
                    continue
            
            if i % 10 == 0 and i > 0:
                print(f"   已等待 {i} 秒...")
                print("   请点击扩展图标 → 选择'自选基金助手'")
            
            await asyncio.sleep(1)
        
        print("\n❌ 等待超时")
        print("\n💡 提示：")
        print("   如果扩展没有显示，请检查：")
        print("   1. 扩展是否已正确加载")
        print("   2. 扩展开关是否已打开")
        print("   3. 是否在扩展管理页面中看到'自选基金助手'")
        
        return self._try_fallback_method()
    
    async def _try_fallback_method(self):
        """备用方法：尝试查找已存在的扩展页面"""
        try:
            print("\n🔄 尝试备用方法...")
            
            pages = self.context.pages
            for page in pages:
                try:
                    url = page.url
                    print(f"   检查页面: {url}")
                    
                    if url.startswith("chrome-extension://"):
                        print(f"   ✅ 找到扩展页面: {url}")
                        self.page = page
                        await self.take_screenshot("extension_page_found.png")
                        return True
                except:
                    continue
            
            print("\n📋 当前打开的页面：")
            for i, page in enumerate(self.context.pages):
                try:
                    print(f"   [{i}] {page.url}")
                except:
                    print(f"   [{i}] (无法获取URL)")
            
            return False
            
        except Exception as e:
            print(f"   备用方法失败: {e}")
            return False
    
    async def open_extension_popup(self):
        """旧方法，保留以兼容现有代码"""
        return await self.open_extension_via_menu()
    
    async def click_fund_compare_button(self):
        try:
            print("查找并点击'基金对比'按钮...")
            
            compare_button = await self.page.query_selector('input[value="基金对比"]')
            if not compare_button:
                compare_button = await self.page.query_selector('button:has-text("基金对比")')
            if not compare_button:
                compare_button = await self.page.query_selector('.btn:has-text("基金对比")')
            
            if compare_button:
                await compare_button.click()
                await asyncio.sleep(2)
                print("已点击'基金对比'按钮")
                return True
            else:
                print("警告: 未找到'基金对比'按钮")
                return False
                
        except Exception as e:
            print(f"点击基金对比按钮失败: {e}")
            return False
    
    async def verify_compare_page(self):
        try:
            print("验证基金对比页面...")
            
            page_title = await self.page.query_selector('h5:has-text("基金对比")')
            if page_title:
                print("基金对比页面标题已显示")
            else:
                print("警告: 未找到基金对比页面标题")
            
            tabs = await self.page.query_selector('.el-tabs')
            if tabs:
                print("标签页组件已加载")
            else:
                print("警告: 未找到标签页组件")
            
            return True
            
        except Exception as e:
            print(f"验证对比页面失败: {e}")
            return False
    
    async def take_screenshot(self, filename):
        try:
            screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            
            filepath = os.path.join(screenshots_dir, filename)
            await self.page.screenshot(path=filepath, full_page=True)
            print(f"截图已保存: {filepath}")
            return filepath
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    async def get_page_content(self):
        try:
            content = await self.page.content()
            return content
        except Exception as e:
            print(f"获取页面内容失败: {e}")
            return ""
    
    async def wait_for_element(self, selector, timeout=10000):
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            return element
        except Exception as e:
            return None
    
    async def click_element(self, selector):
        try:
            element = await self.page.query_selector(selector)
            if element:
                await element.click()
                return True
            return False
        except Exception as e:
            print(f"点击元素失败: {e}")
            return False
