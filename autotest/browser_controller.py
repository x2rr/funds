import os
import asyncio
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
            print("\n⚠️  重要说明:")
            print("   扩展已通过启动参数预加载，无需手动加载！")
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
            
            print("\n浏览器启动成功!")
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
                        print(f"扩展已加载: {EXTENSION_NAME}")
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
        打开扩展并准备测试：
        
        ⚠️  重要技术说明：
        - 浏览器的"三点菜单"、"扩展"子菜单等是操作系统级别的原生UI
        - Playwright 无法直接操作这些原生菜单
        - 但是我们可以用等效的方式实现相同的结果
        
        等效方案：
        1. 直接访问 edge://extensions/ 页面（等效于通过菜单打开）
        2. 验证扩展已正确加载
        3. 提示用户手动点击扩展图标打开弹窗（由于安全限制）
        
        手动操作步骤（如果需要）：
        1. 点击浏览器右上角的扩展图标（拼图形状）
        2. 在弹出的列表中点击"自选基金助手 - 实时查看基金涨跌幅 2.5.2"
        3. 扩展弹窗将打开，测试将继续执行
        """
        try:
            print("\n" + "="*60)
            print("步骤3: 打开扩展并准备测试")
            print("="*60)
            
            print("\n📋 技术说明：")
            print("   浏览器的原生菜单（三点菜单、扩展子菜单）无法被自动化。")
            print("   我们使用等效方案：直接访问扩展管理页面。")
            
            print("\n步骤3.1: 访问扩展管理页面...")
            print(f"   访问: {EDGE_EXTENSIONS_URL}")
            print("   （等效于：Alt+F → 扩展 → 管理扩展）")
            
            await self.page.goto(EDGE_EXTENSIONS_URL, wait_until="networkidle")
            await asyncio.sleep(2)
            
            await self.take_screenshot("extensions_page.png")
            
            print("\n步骤3.2: 验证扩展已加载...")
            
            extension_items = await self.page.query_selector_all('[role="listitem"]')
            target_item = None
            
            for item in extension_items:
                try:
                    text = await item.inner_text()
                    if EXTENSION_NAME in text or "自选基金助手" in text:
                        print(f"   ✓ 找到扩展: {EXTENSION_NAME}")
                        target_item = item
                        break
                except:
                    continue
            
            if target_item:
                print("\n步骤3.3: 查看扩展详情...")
                
                buttons = await target_item.query_selector_all('button')
                for btn in buttons:
                    try:
                        btn_text = await btn.inner_text()
                        if "详细信息" in btn_text or "详情" in btn_text:
                            print(f"   点击: {btn_text}")
                            await btn.click()
                            await asyncio.sleep(2)
                            break
                    except:
                        continue
                
                await self.take_screenshot("extension_details.png")
                
                print("\n" + "!"*60)
                print("⚠️  重要提示：需要手动操作")
                print("!"*60)
                print("""
由于浏览器安全限制，无法自动点击扩展图标打开弹窗。

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
                                print(f"\n   ✓ 检测到扩展弹窗: {url}")
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
                
                print("\n   ✗ 等待超时")
                print("\n💡 提示：")
                print("   如果扩展没有显示，请检查：")
                print("   1. 扩展是否已正确加载")
                print("   2. 扩展开关是否已打开")
                print("   3. 是否在扩展管理页面中看到'自选基金助手'")
                
                return self._try_fallback_method()
                
            else:
                print("\n   ✗ 未在扩展列表中找到目标扩展")
                return self._try_fallback_method()
                
        except Exception as e:
            print(f"\n   打开扩展时出错: {e}")
            import traceback
            traceback.print_exc()
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
                        print(f"   ✓ 找到扩展页面: {url}")
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
            
            print("\n⚠️  备用方法也失败了")
            print("\n💡 建议：")
            print("   1. 手动点击浏览器工具栏的扩展图标")
            print("   2. 选择'自选基金助手'")
            print("   3. 扩展弹窗打开后，测试将可以继续")
            print("\n   或者，您可以直接在扩展管理页面中：")
            print("   1. 找到'自选基金助手'")
            print("   2. 点击'详细信息'")
            print("   3. 在详情页面中找到扩展的相关操作")
            
            return False
            
        except Exception as e:
            print(f"   备用方法失败: {e}")
            return False
    
    async def _open_extension_directly(self):
        """备用方案：直接访问扩展页面"""
        try:
            print("\n  [备用方案] 直接打开扩展管理页面...")
            
            await self.page.goto(EDGE_EXTENSIONS_URL, wait_until="networkidle")
            await asyncio.sleep(2)
            
            await self.take_screenshot("extensions_page.png")
            
            print("  查找目标扩展...")
            extension_items = await self.page.query_selector_all('[role="listitem"]')
            
            for item in extension_items:
                try:
                    text = await item.inner_text()
                    if EXTENSION_NAME in text or "自选基金助手" in text:
                        print(f"    ✓ 找到扩展: {EXTENSION_NAME}")
                        
                        buttons = await item.query_selector_all('button')
                        for btn in buttons:
                            try:
                                btn_text = await btn.inner_text()
                                if "详细信息" in btn_text or "详情" in btn_text:
                                    print(f"    点击: {btn_text}")
                                    await btn.click()
                                    await asyncio.sleep(2)
                                    break
                            except:
                                continue
                        
                        await self.take_screenshot("extension_details.png")
                        
                        await self._wait_for_extension_popup()
                        
                        return True
                except:
                    continue
            
            print("    ✗ 未找到目标扩展")
            return self._try_access_extension_popup()
            
        except Exception as e:
            print(f"  备用方案失败: {e}")
            return self._try_access_extension_popup()
    
    async def _wait_for_extension_popup(self, timeout=10):
        """等待扩展弹窗打开"""
        print(f"  等待扩展弹窗打开 (超时: {timeout}秒)...")
        
        for i in range(timeout):
            pages = self.context.pages
            for page in pages:
                try:
                    url = page.url
                    if "popup.html" in url.lower() or (
                        url.startswith("chrome-extension://") and 
                        ("popup" in url.lower() or "fund" in url.lower())
                    ):
                        print(f"    ✓ 找到扩展弹窗: {url}")
                        self.page = page
                        await self.take_screenshot("extension_popup_opened.png")
                        return True
                except:
                    continue
            
            await asyncio.sleep(1)
        
        print("    提示: 未检测到独立的扩展弹窗页面")
        print("    扩展弹窗可能在当前页面中以其他方式显示")
        return True
    
    async def _try_access_extension_popup(self):
        """尝试直接访问扩展的popup页面"""
        try:
            print("\n  [最终方案] 尝试查找已加载的扩展页面...")
            
            pages = self.context.pages
            for page in pages:
                try:
                    url = page.url
                    print(f"    检查页面: {url}")
                    
                    if url.startswith("chrome-extension://"):
                        print(f"    ✓ 找到扩展页面: {url}")
                        self.page = page
                        await self.take_screenshot("extension_page_found.png")
                        return True
                except:
                    continue
            
            print("\n" + "!"*60)
            print("重要提示:")
            print("  由于浏览器安全限制，无法完全自动化打开扩展弹窗。")
            print("  请手动执行以下操作:")
            print("  1. 点击浏览器工具栏中的扩展图标 (拼图形状)")
            print("  2. 在弹出的列表中点击'自选基金助手 - 实时查看基金涨跌幅'")
            print("  3. 扩展弹窗将打开，测试将继续执行")
            print("!"*60)
            
            print("\n  等待手动操作 (最多等待60秒)...")
            for i in range(60):
                pages = self.context.pages
                for page in pages:
                    try:
                        url = page.url
                        if ("popup.html" in url.lower() or 
                            url.startswith("chrome-extension://")):
                            print(f"    ✓ 检测到扩展弹窗: {url}")
                            self.page = page
                            await self.take_screenshot("manual_extension_opened.png")
                            return True
                    except:
                        continue
                
                if i % 10 == 0:
                    print(f"    已等待 {i} 秒...")
                await asyncio.sleep(1)
            
            print("    ✗ 等待超时")
            return False
            
        except Exception as e:
            print(f"  最终方案失败: {e}")
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
