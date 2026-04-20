import os
import time
import json
import subprocess
from pathlib import Path
from config import (
    EXTENSION_PATH,
    FUNDS_DIR,
    BUG_REPORTS_DIR,
)


class ExtensionManager:
    def __init__(self):
        self.extension_path = EXTENSION_PATH
        self.funds_dir = FUNDS_DIR
        self.bug_reports_dir = BUG_REPORTS_DIR
        
        os.makedirs(self.bug_reports_dir, exist_ok=True)
    
    def get_extension_id(self):
        manifest_path = os.path.join(self.extension_path, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            return manifest.get("name", "Unknown")
        return None
    
    def build_extension(self):
        try:
            print("开始构建扩展...")
            
            npm_path = self._find_npm()
            if not npm_path:
                print("错误: 未找到 npm，请确保 Node.js 已安装并添加到 PATH")
                return False
            
            print(f"使用 npm: {npm_path}")
            
            print("步骤 1: 安装依赖 (如果需要)...")
            install_cmd = [npm_path, "install", "--legacy-peer-deps"]
            install_result = subprocess.run(
                install_cmd,
                cwd=self.funds_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if install_result.returncode != 0:
                print(f"警告: 依赖安装可能有问题: {install_result.stderr}")
            
            print("步骤 2: 构建项目...")
            build_cmd = [npm_path, "run", "build"]
            build_result = subprocess.run(
                build_cmd,
                cwd=self.funds_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if build_result.returncode != 0:
                print(f"错误: 构建失败: {build_result.stderr}")
                return False
            print("构建成功!")
            
            print("步骤 3: 生成压缩包...")
            zip_cmd = [npm_path, "run", "build-zip"]
            zip_result = subprocess.run(
                zip_cmd,
                cwd=self.funds_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if zip_result.returncode != 0:
                print(f"错误: 生成压缩包失败: {zip_result.stderr}")
                return False
            print("压缩包生成成功!")
            
            return True
            
        except Exception as e:
            print(f"构建扩展时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _find_npm(self):
        npm_locations = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expandvars(r"%APPDATA%\npm\npm.cmd"),
            os.path.expandvars(r"%PROGRAMFILES%\nodejs\npm.cmd"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\nodejs\npm.cmd"),
        ]
        
        for location in npm_locations:
            if os.path.exists(location):
                return location
        
        try:
            result = subprocess.run(
                ["where", "npm"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    return lines[0].strip()
        except:
            pass
        
        return "npm"
    
    def create_bug_report(self, bug_info):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        bug_id = f"bug_{timestamp}"
        
        bug_report = {
            "bug_id": bug_id,
            "timestamp": timestamp,
            "title": bug_info.get("title", "未命名Bug"),
            "description": bug_info.get("description", ""),
            "steps_to_reproduce": bug_info.get("steps", []),
            "expected_result": bug_info.get("expected", ""),
            "actual_result": bug_info.get("actual", ""),
            "severity": bug_info.get("severity", "medium"),
            "component": bug_info.get("component", "unknown"),
            "status": "open",
            "fixed": False,
            "fix_description": "",
        }
        
        bug_file = os.path.join(self.bug_reports_dir, f"{bug_id}.json")
        with open(bug_file, "w", encoding="utf-8") as f:
            json.dump(bug_report, f, ensure_ascii=False, indent=2)
        
        print(f"\nBug报告已创建: {bug_file}")
        print(f"Bug标题: {bug_report['title']}")
        
        return bug_file, bug_report
    
    def get_open_bugs(self):
        bugs = []
        if not os.path.exists(self.bug_reports_dir):
            return bugs
        
        for filename in os.listdir(self.bug_reports_dir):
            if filename.startswith("bug_") and filename.endswith(".json"):
                filepath = os.path.join(self.bug_reports_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    bug = json.load(f)
                if bug.get("status") == "open":
                    bugs.append((filepath, bug))
        
        return bugs
    
    def mark_bug_fixed(self, bug_file, fix_description=""):
        if not os.path.exists(bug_file):
            return False
        
        with open(bug_file, "r", encoding="utf-8") as f:
            bug = json.load(f)
        
        bug["status"] = "fixed"
        bug["fixed"] = True
        bug["fix_description"] = fix_description
        bug["fixed_timestamp"] = time.strftime("%Y%m%d_%H%M%S")
        
        with open(bug_file, "w", encoding="utf-8") as f:
            json.dump(bug, f, ensure_ascii=False, indent=2)
        
        print(f"Bug已标记为修复: {bug_file}")
        return True
    
    def get_all_bugs_summary(self):
        summary = {
            "total": 0,
            "open": 0,
            "fixed": 0,
            "bugs": []
        }
        
        if not os.path.exists(self.bug_reports_dir):
            return summary
        
        for filename in os.listdir(self.bug_reports_dir):
            if filename.startswith("bug_") and filename.endswith(".json"):
                filepath = os.path.join(self.bug_reports_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    bug = json.load(f)
                
                summary["total"] += 1
                if bug.get("status") == "open":
                    summary["open"] += 1
                else:
                    summary["fixed"] += 1
                
                summary["bugs"].append({
                    "id": bug.get("bug_id"),
                    "title": bug.get("title"),
                    "status": bug.get("status"),
                    "severity": bug.get("severity"),
                    "file": filepath
                })
        
        return summary
