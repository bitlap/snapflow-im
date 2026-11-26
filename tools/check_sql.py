#!/usr/bin/env python3
"""验证 SQL 规范；保留既有检查入口供构建命令调用。"""

from pathlib import Path

from sql_policy import check


def main():
    check(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    main()
