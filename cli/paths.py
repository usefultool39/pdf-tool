"""工作区路径：个人 PDF/图片等归档在 12pdffun 根目录下的 archive/ 里。"""
from __future__ import annotations

import os
from pathlib import Path

# 12pdffun 根目录（cli 的上一级）
PKG_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = PKG_ROOT / "archive"


def enter_archive_cwd() -> None:
    """将当前工作目录设为 archive/（不存在则创建），便于脚本里继续使用原来的相对路径。"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    os.chdir(ARCHIVE_DIR)
