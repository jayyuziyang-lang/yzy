#!/usr/bin/env python3
"""
扬说财经 · 质量门禁 v5.0（原quality-check.py已升级）

注意: 此脚本已升级。旧版检查项（人物照片引用等）已被废弃。
新版检查项覆盖 v5.0 的8道硬性门禁。

用法:
  python scripts/gate-check.py                 # 完整检查
  python scripts/gate-check.py --edition 版次   # 指定版次
  python scripts/gate-check.py --date 日期      # 指定日期

返回码: 0=通过, 1=待修复, 2=阻塞(不可发布)
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE_PATH = os.path.join(ROOT, 'scripts', 'gate-check.py')

if os.path.exists(GATE_PATH):
    print('=' * 55)
    print('  [v5.0] 质量门禁已升级')
    print('  旧版 quality-check.py 已废弃')
    print('  正在调用 gate-check.py ...')
    print('=' * 55)
    os.execv(sys.executable, [sys.executable, GATE_PATH] + sys.argv[1:])
else:
    print('错误: scripts/gate-check.py 不存在 -- 门禁系统不完整')
    sys.exit(2)
