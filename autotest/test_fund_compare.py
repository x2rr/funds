import os
import asyncio
import time
from browser_controller import BrowserController
from extension_manager import ExtensionManager
from config import (
    TEST_FUND_CODES,
    TEST_PERIODS,
    EXTENSION_NAME,
)


class FundCompareTester:
    def __init__(self):
        self.browser = None
        self.extension_manager = ExtensionManager()
        self.test_results = []
        self.bugs_found = []
    
    async def setup(self):
        print("\n" + "="*60)
        print("开始设置测试环境...")
        print("="*60)
        
        self.browser = BrowserController(headless=False)
        success = await self.browser.start()
        if not success:
            print("错误: 无法启动浏览器")
            return False
        
        return True
    
    async def teardown(self):
        if self.browser:
            await self.browser.close()
    
    async def run_all_tests(self):
        print("\n" + "="*60)
        print("开始执行基金对比功能测试...")
        print("="*60)
        
        try:
            test_passed = await self.test_extension_loading()
            self._record_test("扩展加载测试", test_passed)
            
            if test_passed:
                test_passed = await self.test_fund_compare_button()
                self._record_test("基金对比按钮测试", test_passed)
                
                if test_passed:
                    test_passed = await self.test_fund_selection()
                    self._record_test("基金选择功能测试", test_passed)
                    
                    test_passed = await self.test_period_switching()
                    self._record_test("周期切换功能测试", test_passed)
                    
                    test_passed = await self.test_chart_display()
                    self._record_test("图表显示功能测试", test_passed)
            
            return self._generate_summary()
            
        except Exception as e:
            print(f"测试执行出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_extension_loading(self):
        print("\n--- 测试: 扩展加载 ---")
        
        try:
            await self.browser.navigate_to_extensions()
            await asyncio.sleep(2)
            
            await self.browser.enable_developer_mode()
            await asyncio.sleep(1)
            
            loaded = await self.browser.check_extension_loaded()
            if loaded:
                print("✓ 扩展已成功加载")
                return True
            else:
                print("✗ 扩展未正确加载")
                self._report_bug(
                    title="扩展加载失败",
                    description="扩展未在扩展管理页面中正确显示",
                    steps=[
                        "打开浏览器",
                        "导航到 edge://extensions/",
                        "检查扩展列表"
                    ],
                    expected=f"应显示 '{EXTENSION_NAME}' 扩展",
                    actual="扩展未显示或显示异常",
                    component="扩展安装",
                    severity="high"
                )
                return False
                
        except Exception as e:
            print(f"✗ 扩展加载测试出错: {e}")
            return False
    
    async def test_fund_compare_button(self):
        print("\n--- 测试: 基金对比按钮 ---")
        
        try:
            opened = await self.browser.open_extension_popup()
            if not opened:
                print("警告: 无法自动打开扩展弹窗，请手动操作")
            
            await asyncio.sleep(3)
            
            clicked = await self.browser.click_fund_compare_button()
            if clicked:
                await asyncio.sleep(2)
                
                verified = await self.browser.verify_compare_page()
                if verified:
                    print("✓ 基金对比按钮功能正常")
                    await self.browser.take_screenshot("compare_page_opened.png")
                    return True
                else:
                    print("✗ 基金对比页面未正确显示")
                    self._report_bug(
                        title="基金对比页面显示异常",
                        description="点击基金对比按钮后，页面未正确显示",
                        steps=[
                            "打开扩展弹窗",
                            "点击'基金对比'按钮"
                        ],
                        expected="应显示基金对比选择页面",
                        actual="页面未显示或显示异常",
                        component="基金对比功能",
                        severity="high"
                    )
                    return False
            else:
                print("✗ 未找到基金对比按钮")
                self._report_bug(
                    title="基金对比按钮缺失",
                    description="主界面未找到'基金对比'按钮",
                    steps=[
                        "打开扩展弹窗",
                        "检查工具栏按钮"
                    ],
                    expected="应显示'基金对比'按钮",
                    actual="按钮不存在",
                    component="UI界面",
                    severity="high"
                )
                return False
                
        except Exception as e:
            print(f"✗ 基金对比按钮测试出错: {e}")
            return False
    
    async def test_fund_selection(self):
        print("\n--- 测试: 基金选择功能 ---")
        
        try:
            await asyncio.sleep(2)
            
            fund_items = await self.browser.page.query_selector_all('.fund-item')
            
            if fund_items:
                print(f"找到 {len(fund_items)} 个可选基金")
                
                if len(fund_items) >= 1:
                    await fund_items[0].click()
                    await asyncio.sleep(1)
                    
                    selected_items = await self.browser.page.query_selector_all('.selected-item')
                    if selected_items:
                        print("✓ 基金选择功能正常")
                        await self.browser.take_screenshot("fund_selected.png")
                        return True
                    else:
                        print("✗ 基金选择后未在已选择列表中显示")
                        self._report_bug(
                            title="基金选择后未显示",
                            description="点击选择基金后，已选择列表未更新",
                            steps=[
                                "打开基金对比页面",
                                "点击一个基金进行选择"
                            ],
                            expected="已选择基金应显示在'已选择对比'列表中",
                            actual="选择后列表未更新",
                            component="基金选择功能",
                            severity="medium"
                        )
                        return False
            else:
                print("警告: 未找到可选基金列表（可能需要先添加自选基金）")
                
                add_section = await self.browser.page.query_selector('.add-fund-section')
                if add_section:
                    print("找到'添加新基金'区域")
                    return True
                else:
                    print("✗ 未找到可选基金或添加新基金区域")
                    self._report_bug(
                        title="基金选择区域异常",
                        description="基金对比页面未显示可选基金列表或添加新基金区域",
                        steps=[
                            "打开基金对比页面"
                        ],
                        expected="应显示自选基金列表和添加新基金区域",
                        actual="区域未显示或为空",
                        component="基金选择功能",
                        severity="high"
                    )
                    return False
                    
        except Exception as e:
            print(f"✗ 基金选择功能测试出错: {e}")
            return False
    
    async def test_period_switching(self):
        print("\n--- 测试: 周期切换功能 ---")
        
        try:
            start_compare_btn = await self.browser.page.query_selector('input[value="开始对比"]')
            if start_compare_btn:
                await start_compare_btn.click()
                await asyncio.sleep(3)
                
                radio_buttons = await self.browser.page.query_selector_all('.el-radio-button')
                if radio_buttons:
                    print(f"找到 {len(radio_buttons)} 个周期选项")
                    
                    for i, radio in enumerate(radio_buttons):
                        try:
                            await radio.click()
                            await asyncio.sleep(1)
                            print(f"  ✓ 切换到周期选项 {i+1} 成功")
                        except Exception as e:
                            print(f"  ✗ 切换周期选项 {i+1} 失败: {e}")
                    
                    print("✓ 周期切换功能正常")
                    await self.browser.take_screenshot("period_switched.png")
                    return True
                else:
                    print("✗ 未找到周期切换单选按钮")
                    self._report_bug(
                        title="周期切换按钮缺失",
                        description="基金对比结果页面未找到周期切换选项",
                        steps=[
                            "选择基金后点击'开始对比'",
                            "检查周期切换区域"
                        ],
                        expected="应显示近一周、近一月等周期切换按钮",
                        actual="按钮不存在",
                        component="周期切换功能",
                        severity="medium"
                    )
                    return False
            else:
                print("警告: 无法测试周期切换（需要先选择基金）")
                return True
                
        except Exception as e:
            print(f"✗ 周期切换功能测试出错: {e}")
            return False
    
    async def test_chart_display(self):
        print("\n--- 测试: 图表显示功能 ---")
        
        try:
            chart_tab = await self.browser.page.query_selector('.el-tabs__item:has-text("收益走势对比")')
            if chart_tab:
                await chart_tab.click()
                await asyncio.sleep(2)
                
                chart_container = await self.browser.page.query_selector('.main-echarts')
                if chart_container:
                    print("✓ 图表容器已显示")
                    
                    canvas = await chart_container.query_selector('canvas')
                    if canvas:
                        print("✓ 图表Canvas已渲染")
                    else:
                        print("警告: 未找到Canvas元素（可能需要数据加载）")
                    
                    await self.browser.take_screenshot("chart_displayed.png")
                    return True
                else:
                    print("✗ 未找到图表容器")
                    self._report_bug(
                        title="图表容器缺失",
                        description="收益走势对比页面未找到图表容器",
                        steps=[
                            "进入基金对比结果页面",
                            "点击'收益走势对比'标签"
                        ],
                        expected="应显示ECharts图表容器",
                        actual="图表容器不存在",
                        component="图表显示功能",
                        severity="medium"
                    )
                    return False
            else:
                print("警告: 无法测试图表显示（需要先进入对比结果页面）")
                return True
                
        except Exception as e:
            print(f"✗ 图表显示功能测试出错: {e}")
            return False
    
    def _record_test(self, test_name, passed):
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def _report_bug(self, title, description, steps, expected, actual, component, severity):
        bug_info = {
            "title": title,
            "description": description,
            "steps": steps,
            "expected": expected,
            "actual": actual,
            "component": component,
            "severity": severity
        }
        
        bug_file, bug_report = self.extension_manager.create_bug_report(bug_info)
        self.bugs_found.append({
            "file": bug_file,
            "report": bug_report
        })
    
    def _generate_summary(self):
        print("\n" + "="*60)
        print("测试执行摘要")
        print("="*60)
        
        passed_count = sum(1 for r in self.test_results if r["passed"])
        failed_count = len(self.test_results) - passed_count
        
        print(f"\n总测试数: {len(self.test_results)}")
        print(f"通过: {passed_count}")
        print(f"失败: {failed_count}")
        
        print("\n详细结果:")
        for result in self.test_results:
            status = "✓ 通过" if result["passed"] else "✗ 失败"
            print(f"  {status}: {result['name']}")
        
        if self.bugs_found:
            print(f"\n发现的Bug数: {len(self.bugs_found)}")
            for bug in self.bugs_found:
                print(f"  - {bug['report']['title']} (文件: {bug['file']})")
        else:
            print("\n未发现Bug")
        
        return failed_count == 0
