import asyncio
import os
import sys
import json
from test_fund_compare import FundCompareTester
from extension_manager import ExtensionManager
from config import BUG_REPORTS_DIR


class AutoTestRunner:
    def __init__(self):
        self.extension_manager = ExtensionManager()
        self.max_iterations = 5
        self.current_iteration = 0
    
    async def run(self):
        print("="*70)
        print("自选基金助手 - 自动化测试脚本")
        print("="*70)
        print(f"\n工作目录: {os.getcwd()}")
        print(f"扩展路径: {self.extension_manager.extension_path}")
        print(f"Bug报告目录: {BUG_REPORTS_DIR}")
        
        print("\n" + "="*70)
        print("测试流程说明:")
        print("="*70)
        print("""
📋 技术架构说明：
─────────────────────────────────────────────────────────────
  本测试脚本使用两种自动化技术：
  
  1. Playwright: 用于操作网页 DOM 元素
     - 导航网页、点击按钮、填写表单
     - 截图、验证页面内容
     
  2. pywinauto: 用于操作 Windows 原生 UI ✨ 新增
     - 点击浏览器工具栏图标
     - 操作浏览器菜单（三点菜单、扩展子菜单）
     - 点击弹出窗口中的选项

完整测试流程：
┌─────────────────────────────────────────────────────────────┐
│ 步骤1: 打开浏览器，加载扩展                                  │
│   - 启动Edge浏览器                                           │
│   - 通过启动参数自动预加载扩展（无需手动加载）                │
│   - 扩展路径: D:\fund_helper\funds\dist-zip\choose-funds-v2.5.2 │
│   - 连接 pywinauto 控制器                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤2: 验证扩展加载状态                                      │
│   - 导航到扩展管理页面 (edge://extensions/)                  │
│   - 验证'自选基金助手'扩展是否已正确显示                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤3: 通过菜单打开扩展并测试功能 ✨ pywinauto 自动化       │
│                                                              │
│  🎯 使用 pywinauto 自动操作：                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  方法1（推荐）: 点击工具栏扩展图标                    │   │
│  │  1. 点击工具栏中的扩展图标（拼图形状）                │   │
│  │  2. 在弹出的列表中点击"自选基金助手"                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  方法2（备选）: 通过三点菜单                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 点击右上角的三个点（设置及其他）                  │   │
│  │  2. 在菜单中点击"扩展"                                │   │
│  │  3. 在扩展列表中点击"自选基金助手"                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  🔍 测试内容：                                               │
│     ① 工具栏对比按钮是否正常显示                             │
│     ② 自选基金选择功能是否正常                               │
│     ③ 新增基金搜索功能是否正常                               │
│     ④ 对比周期切换是否正常 (近一周/一月/三月/一年/三年)     │
│     ⑤ 收益率对比表格是否正确显示                             │
│     ⑥ 收益走势图表是否正常渲染                               │
│                                                              │
│  🐛 发现Bug时自动生成Bug报告                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤4: 读取Bug报告并修复                                     │
│   - 自动分析Bug报告                                          │
│   - 尝试自动修复简单问题                                     │
│   - 生成修复指南供手动修复                                    │
│   - 重新构建扩展 (npm run build / npm run build-zip)        │
│   - 标记Bug修复情况                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤5: 循环测试 (最多5次)                                    │
│   - 重复执行步骤2-4                                          │
│   - 直到没有未修复的Bug或达到最大循环次数                     │
└─────────────────────────────────────────────────────────────┘
""")
        
        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            print(f"\n{'='*70}")
            print(f"第 {self.current_iteration} 次测试循环")
            print(f"{'='*70}")
            
            print("\n步骤 1 & 2: 启动浏览器并验证扩展加载...")
            tester = FundCompareTester()
            try:
                setup_ok = await tester.setup()
                if not setup_ok:
                    print("错误: 测试环境设置失败")
                    break
                
                test_passed = await tester.run_all_tests()
                
                await tester.teardown()
                
            except Exception as e:
                print(f"测试执行出错: {e}")
                import traceback
                traceback.print_exc()
                test_passed = False
            
            print("\n步骤 4: 检查是否有未修复的Bug...")
            open_bugs = self.extension_manager.get_open_bugs()
            
            if not open_bugs:
                print("\n" + "="*70)
                print("所有测试通过，没有未修复的Bug!")
                print("="*70)
                self._print_final_summary()
                return True
            
            print(f"\n发现 {len(open_bugs)} 个未修复的Bug")
            
            print("\n步骤 4: 分析并修复Bug...")
            await self._analyze_and_fix_bugs(open_bugs)
            
            print("\n步骤 4: 重新构建扩展...")
            build_ok = self.extension_manager.build_extension()
            
            if not build_ok:
                print("警告: 构建失败，继续下一次循环...")
                continue
            
            print("\n步骤 5: 准备下一次测试循环...")
        
        print("\n" + "="*70)
        print(f"已达到最大循环次数 ({self.max_iterations})，测试结束")
        print("="*70)
        self._print_final_summary()
        return False
    
    async def _analyze_and_fix_bugs(self, open_bugs):
        for bug_file, bug in open_bugs:
            print(f"\n分析Bug: {bug['title']}")
            print(f"  严重程度: {bug['severity']}")
            print(f"  组件: {bug['component']}")
            print(f"  描述: {bug['description']}")
            
            fix_applied = await self._attempt_fix(bug)
            
            if fix_applied:
                self.extension_manager.mark_bug_fixed(
                    bug_file,
                    fix_description="已应用自动化修复"
                )
            else:
                print(f"  提示: 此Bug需要手动修复")
                self._generate_fix_guide(bug_file, bug)
    
    async def _attempt_fix(self, bug):
        title = bug.get("title", "").lower()
        component = bug.get("component", "").lower()
        
        if "manifest" in title or "版本" in title:
            return await self._fix_manifest_version()
        
        elif "按钮" in title or "缺失" in title:
            return await self._check_ui_components()
        
        elif "图表" in title:
            return await self._check_chart_components()
        
        return False
    
    async def _fix_manifest_version(self):
        try:
            manifest_path = os.path.join(
                self.extension_manager.funds_dir,
                "src",
                "manifest.json"
            )
            
            if os.path.exists(manifest_path):
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                
                if manifest.get("version") is None:
                    package_path = os.path.join(
                        self.extension_manager.funds_dir,
                        "package.json"
                    )
                    
                    if os.path.exists(package_path):
                        with open(package_path, "r", encoding="utf-8") as f:
                            package = json.load(f)
                        
                        manifest["version"] = package.get("version", "2.5.2")
                        
                        with open(manifest_path, "w", encoding="utf-8") as f:
                            json.dump(manifest, f, ensure_ascii=False, indent=2)
                        
                        print("  ✓ 已修复 manifest.json 中的版本号")
                        return True
            
            return False
        except Exception as e:
            print(f"  ✗ 修复 manifest 失败: {e}")
            return False
    
    async def _check_ui_components(self):
        print("  检查UI组件配置...")
        return False
    
    async def _check_chart_components(self):
        print("  检查图表组件配置...")
        return False
    
    def _generate_fix_guide(self, bug_file, bug):
        guide_file = bug_file.replace(".json", "_fix_guide.txt")
        
        guide_content = f"""
Bug修复指南
==========

Bug ID: {bug.get('bug_id', 'N/A')}
标题: {bug.get('title', 'N/A')}
严重程度: {bug.get('severity', 'N/A')}
组件: {bug.get('component', 'N/A')}

问题描述:
{bug.get('description', 'N/A')}

预期结果:
{bug.get('expected', 'N/A')}

实际结果:
{bug.get('actual', 'N/A')}

复现步骤:
{chr(10).join(f'  {i+1}. {step}' for i, step in enumerate(bug.get('steps_to_reproduce', [])))}

建议修复方向:
--------------

1. 检查相关文件:
   - src/popup/App.vue (主界面)
   - src/common/fundCompareSelect.vue (基金选择)
   - src/common/fundCompareResult.vue (对比结果)
   - src/manifest.json (扩展配置)

2. 可能的问题类型:
   - UI组件未正确渲染
   - 事件绑定问题
   - 数据加载失败
   - 样式问题
   - 扩展权限问题

3. 调试建议:
   - 使用浏览器开发者工具检查控制台错误
   - 检查网络请求是否成功
   - 验证Vue组件是否正确挂载
   - 检查Element UI组件是否正确导入

手动修复步骤:
-------------
1. 分析Bug报告，定位问题代码
2. 修改相关文件
3. 运行构建命令:
   cd D:\fund_helper\funds
   npm run build
   npm run build-zip

4. 重新运行此测试脚本验证修复

"""
        
        with open(guide_file, "w", encoding="utf-8") as f:
            f.write(guide_content)
        
        print(f"  已生成修复指南: {guide_file}")
    
    def _print_final_summary(self):
        summary = self.extension_manager.get_all_bugs_summary()
        
        print(f"\n最终测试摘要:")
        print(f"  总测试循环数: {self.current_iteration}")
        print(f"  总Bug数: {summary['total']}")
        print(f"  已修复: {summary['fixed']}")
        print(f"  待修复: {summary['open']}")
        
        if summary['bugs']:
            print(f"\nBug详情:")
            for bug in summary['bugs']:
                status = "✓ 已修复" if bug['status'] == 'fixed' else "✗ 待修复"
                print(f"  {status}: {bug['title']}")
        
        print(f"\nBug报告目录: {BUG_REPORTS_DIR}")


async def main():
    runner = AutoTestRunner()
    success = await runner.run()
    
    if success:
        print("\n✓ 自动化测试完成，所有功能正常!")
        sys.exit(0)
    else:
        print("\n✗ 自动化测试完成，但存在需要手动修复的问题")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
