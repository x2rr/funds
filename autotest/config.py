import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNDS_DIR = os.path.join(PROJECT_ROOT, "funds")
EXTENSION_PATH = os.path.join(FUNDS_DIR, "dist-zip", "choose-funds-v2.5.2")
EXTENSION_ZIP = os.path.join(FUNDS_DIR, "dist-zip", "choose-funds-v2.5.2.zip")
BUG_REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bug_reports")

EDGE_EXTENSIONS_URL = "edge://extensions/"
CHROME_EXTENSIONS_URL = "chrome://extensions/"

EXTENSION_NAME = "自选基金助手 - 实时查看基金涨跌幅"
EXTENSION_VERSION = "2.5.2"

TEST_FUND_CODES = [
    "000001",
    "110022",
    "161725",
]

TEST_PERIODS = [
    "week",
    "month",
    "3month",
    "year",
    "3year",
]
