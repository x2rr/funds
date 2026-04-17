import os
import time
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
            
            self.browser = await self.playwright.chromium.launch(
                executable_path=edge_executable,
                headless=self.headless,
                args=args,
            )
            
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            
            self.page = await self.context.new_page()
            
            print("浏览器启动成功!")
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
    
    async def open_extension_popup(self):
        try:
            print("尝试打开扩展弹窗...")
            
            extension_pages = self.context.pages
            for page in extension_pages:
                try:
                    url = page.url
                    if "extension" in url.lower() or "popup" in url.lower():
                        print(f"找到扩展页面: {url}")
                        self.page = page
                        return True
                except:
                    continue
            
            print("尝试通过Chrome URL方案访问扩展...")
            try:
                await self.page.goto("chrome://extensions/", wait_until="networkidle")
                await asyncio.sleep(2)
                
                extension_items = await self.page.query_selector_all('extension-item, .extension-item')
                for item in extension_items:
                    try:
                        text = await item.inner_text()
                        if EXTENSION_NAME in text or "自选基金" in text:
                            details_button = await item.query_selector('button[aria-label*="详情"], button:has-text("详情")')
                            if details_button:
                                await details_button.click()
                                await asyncio.sleep(1)
                                break
                    except:
                        continue
            except Exception as e:
                print(f"访问扩展详情失败: {e}")
            
            print("提示: 扩展弹窗需要手动点击扩展图标打开")
            print("请手动点击浏览器工具栏中的扩展图标，然后选择'自选基金助手'")
            await asyncio.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"打开扩展弹窗失败: {e}")
            return False
    
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
