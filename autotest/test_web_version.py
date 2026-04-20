"""
Web版自选基金助手 - 自动化测试脚本
=====================================

这个脚本用于测试Web版本的自选基金助手。
与插件版不同，Web版可以直接用Playwright操作DOM，无需操作系统级菜单。

测试流程：
1. 启动本地HTTP服务器（可选）
2. 导航到Web页面
3. 验证页面加载和基础功能
4. 测试各项功能：
   - 基金管理（添加、删除）
   - 行情中心
   - 设置页面
   - 数据导入导出
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from playwright.async_api import async_playwright


class WebFundTester:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "funds", "web")
        self.base_url = None
        self.results = []
        self.screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    async def setup(self, use_server: bool = True, port: int = 8080):
        """
        设置测试环境
        
        Args:
            use_server: 是否使用HTTP服务器（推荐）
            port: HTTP服务器端口
        """
        print("\n" + "="*70)
        print("Web版自选基金助手 - 测试环境设置")
        print("="*70)
        
        if not os.path.exists(self.web_path):
            print(f"错误: Web目录不存在: {self.web_path}")
            return False
        
        index_path = os.path.join(self.web_path, "index.html")
        if not os.path.exists(index_path):
            print(f"错误: index.html不存在: {index_path}")
            return False
        
        print(f"✓ Web目录: {self.web_path}")
        
        try:
            self.playwright = await async_playwright().start()
            
            print("✓ 启动浏览器...")
            self.browser = await self.playwright.chromium.launch(headless=False)
            
            self.context = await self.browser.new_context(
                viewport={'width': 1200, 'height': 800}
            )
            
            self.page = await self.context.new_page()
            
            if use_server:
                import subprocess
                import threading
                import time
                
                print(f"✓ 启动HTTP服务器 (端口 {port})...")
                
                server_cwd = self.web_path
                self.server_process = subprocess.Popen(
                    [sys.executable, "-m", "http.server", str(port)],
                    cwd=server_cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                time.sleep(1)
                
                self.base_url = f"http://localhost:{port}"
                print(f"✓ HTTP服务器地址: {self.base_url}")
            else:
                self.base_url = f"file://{index_path}"
                print(f"✓ 使用本地文件URL: {self.base_url}")
            
            return True
            
        except Exception as e:
            print(f"✗ 设置测试环境失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def teardown(self):
        """清理测试环境"""
        print("\n✓ 清理测试环境...")
        
        if hasattr(self, 'server_process') and self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        
        if self.page:
            await self.page.close()
        
        if self.context:
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
        
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        print("✓ 测试环境已清理")
    
    def _record_result(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {status}: {test_name}")
        if message:
            print(f"     详情: {message}")
    
    async def _take_screenshot(self, name: str):
        """截图"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        await self.page.screenshot(path=filepath)
        print(f"  📸 截图已保存: {filename}")
        return filepath
    
    async def test_page_load(self):
        """测试页面加载"""
        print("\n测试 1: 页面加载测试")
        print("-"*70)
        
        try:
            print(f"  导航到: {self.base_url}")
            await self.page.goto(self.base_url, wait_until='networkidle')
            
            await self._take_screenshot("page_load_initial")
            
            title = await self.page.title()
            print(f"  页面标题: {title}")
            
            if "自选基金助手" in title:
                self._record_result("页面标题验证", True, f"标题: {title}")
            else:
                self._record_result("页面标题验证", False, f"预期包含'自选基金助手',实际为: {title}")
                return False
            
            loading_visible = await self.page.locator('.loading-mask').is_visible()
            if loading_visible:
                print("  等待加载完成...")
                await self.page.wait_for_selector('.loading-mask', state='hidden', timeout=10000)
            
            await self._take_screenshot("page_load_complete")
            
            nav_items = await self.page.locator('.nav-item').all()
            nav_count = len(nav_items)
            self._record_result(
                "导航栏验证", 
                nav_count >= 4, 
                f"导航项数量: {nav_count}"
            )
            
            expected_navs = ["基金管理", "行情中心", "设置", "关于"]
            for nav_text in expected_navs:
                nav_visible = await self.page.locator(f'.nav-item:text("{nav_text}")').is_visible()
                self._record_result(f"导航项 '{nav_text}' 存在", nav_visible)
            
            return True
            
        except Exception as e:
            self._record_result("页面加载测试", False, str(e))
            await self._take_screenshot("page_load_error")
            return False
    
    async def test_navigation(self):
        """测试导航切换"""
        print("\n测试 2: 导航切换测试")
        print("-"*70)
        
        try:
            nav_tests = [
                ("基金管理", ".action-bar", "操作按钮区域"),
                ("行情中心", ".section-title:text('主要指数')", "主要指数标题"),
                ("设置", ".section-title:text('显示设置')", "显示设置标题"),
                ("关于", ".section-title:text('关于自选基金助手')", "关于标题"),
            ]
            
            for nav_text, check_selector, check_desc in nav_tests:
                print(f"  测试导航到: {nav_text}")
                
                nav_item = self.page.locator(f'.nav-item:text("{nav_text}")')
                await nav_item.click()
                
                await self.page.wait_for_timeout(500)
                
                check_element = self.page.locator(check_selector)
                is_visible = await check_element.is_visible()
                
                self._record_result(
                    f"导航到 '{nav_text}'", 
                    is_visible, 
                    f"验证{check_desc}"
                )
                
                await self._take_screenshot(f"nav_{nav_text}")
            
            await self.page.locator('.nav-item:text("基金管理")').click()
            
            return True
            
        except Exception as e:
            self._record_result("导航切换测试", False, str(e))
            await self._take_screenshot("navigation_error")
            return False
    
    async def test_edit_mode(self):
        """测试编辑模式"""
        print("\n测试 3: 编辑模式测试")
        print("-"*70)
        
        try:
            await self.page.locator('.nav-item:text("基金管理")').click()
            await self.page.wait_for_timeout(500)
            
            edit_btn = self.page.locator('.btn:text("编辑")')
            edit_visible = await edit_btn.is_visible()
            self._record_result("编辑按钮存在", edit_visible)
            
            if edit_visible:
                await edit_btn.click()
                await self.page.wait_for_timeout(500)
                
                add_section = self.page.locator('.add-fund-section')
                add_visible = await add_section.is_visible()
                self._record_result("编辑模式激活", add_visible, "添加基金区域显示")
                
                await self._take_screenshot("edit_mode")
                
                done_btn = self.page.locator('.btn:text("完成编辑")')
                done_visible = await done_btn.is_visible()
                self._record_result("完成编辑按钮存在", done_visible)
                
                if done_visible:
                    await done_btn.click()
                    await self.page.wait_for_timeout(500)
                    
                    add_hidden = not await add_section.is_visible()
                    self._record_result("退出编辑模式", add_hidden, "添加基金区域隐藏")
                
                await self._take_screenshot("edit_mode_done")
            
            return True
            
        except Exception as e:
            self._record_result("编辑模式测试", False, str(e))
            await self._take_screenshot("edit_mode_error")
            return False
    
    async def test_dark_mode(self):
        """测试深色模式"""
        print("\n测试 4: 深色模式测试")
        print("-"*70)
        
        try:
            await self.page.locator('.nav-item:text("设置")').click()
            await self.page.wait_for_timeout(500)
            
            dark_mode_switch = self.page.locator('.el-switch')
            switch_visible = await dark_mode_switch.is_visible()
            self._record_result("深色模式开关存在", switch_visible)
            
            if switch_visible:
                dark_mode_checked = await dark_mode_switch.get_attribute('class')
                is_checked = 'is-checked' in (dark_mode_checked or '')
                
                if not is_checked:
                    await dark_mode_switch.click()
                    await self.page.wait_for_timeout(500)
                
                dark_mode_active = await self.page.locator('.dark-mode').is_visible()
                self._record_result(
                    "深色模式激活", 
                    dark_mode_active, 
                    "dark-mode 类名存在"
                )
                
                await self._take_screenshot("dark_mode")
                
                dark_mode_checked_after = await dark_mode_switch.get_attribute('class')
                is_checked_after = 'is-checked' in (dark_mode_checked_after or '')
                
                if is_checked_after:
                    await dark_mode_switch.click()
                    await self.page.wait_for_timeout(500)
                
                await self._take_screenshot("light_mode")
            
            return True
            
        except Exception as e:
            self._record_result("深色模式测试", False, str(e))
            await self._take_screenshot("dark_mode_error")
            return False
    
    async def test_fund_search(self):
        """测试基金搜索功能"""
        print("\n测试 5: 基金搜索功能测试")
        print("-"*70)
        
        try:
            await self.page.locator('.nav-item:text("基金管理")').click()
            await self.page.wait_for_timeout(500)
            
            edit_btn = self.page.locator('.btn:text("编辑")')
            if await edit_btn.is_visible():
                await edit_btn.click()
                await self.page.wait_for_timeout(500)
            
            search_box = self.page.locator('.el-select')
            search_visible = await search_box.is_visible()
            self._record_result("基金搜索框存在", search_visible)
            
            if search_visible:
                await search_box.click()
                await self.page.wait_for_timeout(300)
                
                search_input = self.page.locator('.el-select .el-input__inner')
                await search_input.fill('000001')
                await self.page.wait_for_timeout(1000)
                
                await self._take_screenshot("fund_search")
                
                options = await self.page.locator('.el-select-dropdown__item').all()
                option_count = len(options)
                self._record_result(
                    "基金搜索结果", 
                    option_count > 0, 
                    f"搜索结果数量: {option_count}"
                )
            
            return True
            
        except Exception as e:
            self._record_result("基金搜索测试", False, str(e))
            await self._take_screenshot("fund_search_error")
            return False
    
    async def test_market_data(self):
        """测试行情数据"""
        print("\n测试 6: 行情数据测试")
        print("-"*70)
        
        try:
            await self.page.locator('.nav-item:text("行情中心")').click()
            await self.page.wait_for_timeout(500)
            
            index_cards = await self.page.locator('.tab-col').all()
            index_count = len(index_cards)
            self._record_result(
                "指数卡片显示", 
                index_count >= 4, 
                f"指数数量: {index_count}"
            )
            
            if index_count > 0:
                first_index_name = await index_cards[0].locator('h5').text_content()
                first_index_change = await index_cards[0].locator('p').nth(1).text_content()
                self._record_result(
                    "指数数据显示", 
                    True, 
                    f"首个指数: {first_index_name}, 涨跌幅: {first_index_change}"
                )
            
            await self._take_screenshot("market_data")
            
            return True
            
        except Exception as e:
            self._record_result("行情数据测试", False, str(e))
            await self._take_screenshot("market_data_error")
            return False
    
    async def test_refresh_button(self):
        """测试刷新按钮"""
        print("\n测试 7: 刷新按钮测试")
        print("-"*70)
        
        try:
            refresh_btn = self.page.locator('.refresh-btn')
            btn_visible = await refresh_btn.is_visible()
            self._record_result("刷新按钮存在", btn_visible)
            
            if btn_visible:
                await refresh_btn.click()
                await self.page.wait_for_timeout(1000)
                
                await self._take_screenshot("refresh_click")
                self._record_result("刷新按钮点击", True)
            
            return True
            
        except Exception as e:
            self._record_result("刷新按钮测试", False, str(e))
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("开始运行所有测试")
        print("="*70)
        
        tests = [
            ("页面加载", self.test_page_load),
            ("导航切换", self.test_navigation),
            ("编辑模式", self.test_edit_mode),
            ("深色模式", self.test_dark_mode),
            ("基金搜索", self.test_fund_search),
            ("行情数据", self.test_market_data),
            ("刷新按钮", self.test_refresh_button),
        ]
        
        passed_count = 0
        failed_count = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"  测试 '{test_name}' 执行出错: {e}")
                failed_count += 1
        
        print("\n" + "="*70)
        print("测试结果汇总")
        print("="*70)
        print(f"  总测试数: {len(tests)}")
        print(f"  通过: {passed_count}")
        print(f"  失败: {failed_count}")
        print(f"  成功率: {passed_count/len(tests)*100:.1f}%")
        
        print("\n详细结果:")
        for result in self.results:
            status = "✓" if result["passed"] else "✗"
            print(f"  {status} {result['test_name']}: {result['message'] or '无消息'}")
        
        return failed_count == 0


async def main():
    """主函数"""
    print("="*70)
    print("Web版自选基金助手 - 自动化测试脚本")
    print("="*70)
    print(f"\n工作目录: {os.getcwd()}")
    print(f"测试类型: Web版本（无需操作系统级菜单）")
    print("""
🎯 测试优势（对比插件版）：
  - 无需使用 pywinauto 操作系统级菜单
  - 直接用 Playwright 操作 DOM 元素
  - 更稳定、更快速的测试
  - 支持所有现代浏览器

📋 测试内容：
  1. 页面加载验证
  2. 导航切换功能
  3. 编辑模式测试
  4. 深色模式切换
  5. 基金搜索功能
  6. 行情数据显示
  7. 刷新按钮功能
""")
    
    tester = WebFundTester()
    
    try:
        setup_ok = await tester.setup(use_server=True, port=8080)
        
        if not setup_ok:
            print("\n错误: 测试环境设置失败")
            return False
        
        test_passed = await tester.run_all_tests()
        
        return test_passed
        
    except Exception as e:
        print(f"\n测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await tester.teardown()


if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n✓ 所有Web版测试通过!")
        sys.exit(0)
    else:
        print("\n✗ Web版测试存在失败项")
        sys.exit(1)
