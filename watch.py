#!/usr/bin/env python3
"""监听 src/ 与 build.py 的改动，自动重新生成 index.html / pc.html。
用法：python3 watch.py   （Ctrl+C 退出）"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
WATCH = [ROOT / "src" / "template.html", ROOT / "src" / "pc-template.html", ROOT / "build.py"]


def stamp():
    return tuple(p.stat().st_mtime if p.exists() else 0 for p in WATCH)


def build():
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=ROOT)
    print("✅ 已重新生成" if r.returncode == 0 else "❌ 生成失败，看上面的报错", flush=True)


print("👀 正在监听 src/ 改动，保存即自动生成…（Ctrl+C 退出）", flush=True)
build()
last = stamp()
while True:
    time.sleep(1)
    cur = stamp()
    if cur != last:
        last = cur
        build()
