#!/usr/bin/env python3
"""
零碳能源知识库 - 审核工具
用法：
  python3 review.py --show           # 查看待审列表（按分类汇总）
  python3 review.py --show --keyword 抽水蓄能   # 查看某关键词的待审项
  python3 review.py --approve-all    # 批量通过所有 pending 条目
  python3 review.py --export         # 导出已通过的条目为 CSV
"""

import json
import argparse
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
REVIEW_FILE = BASE_DIR / "review_index.json"


def load():
    if not REVIEW_FILE.exists():
        print("❌ review_index.json 不存在，请先运行 crawler.py")
        return None
    with open(REVIEW_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    data["updated_at"] = datetime.now().isoformat()
    items = data["items"]
    data["stats"] = {
        "total": len(items),
        "pending": sum(1 for x in items if x["review_status"] == "pending"),
        "approved": sum(1 for x in items if x["review_status"] == "approved"),
        "rejected": sum(1 for x in items if x["review_status"] == "rejected"),
    }
    with open(REVIEW_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_summary(data, keyword=None):
    items = data["items"]
    if keyword:
        items = [x for x in items if x.get("keyword") == keyword]

    print(f"\n{'='*60}")
    print(f"📋 标准索引统计 (共 {len(items)} 条)")
    print(f"{'='*60}")

    # 按分类+关键词分组
    groups = {}
    for item in items:
        key = f"{item.get('category','?')} > {item.get('keyword','?')}"
        groups.setdefault(key, {"pending": [], "approved": [], "rejected": []})
        groups[key][item["review_status"]].append(item)

    for group_key, statuses in sorted(groups.items()):
        pending = len(statuses["pending"])
        approved = len(statuses["approved"])
        total = sum(len(v) for v in statuses.values())
        print(f"\n📁 {group_key}  [{total}条]")

        for status_label, status_items in [("待审", statuses["pending"]), ("✅通过", statuses["approved"]), ("❌拒绝", statuses["rejected"])]:
            if not status_items:
                continue
            print(f"  {status_label}({len(status_items)}):")
            for item in status_items[:5]:
                phase = item.get("phase", "?")
                std_type = item.get("std_type", "?")
                print(f"    [{phase}/{std_type}] {item['code']} {item['title'][:40]}")
                print(f"      状态:{item['status']}  {item['detail_url']}")
            if len(status_items) > 5:
                print(f"    ... 还有 {len(status_items)-5} 条")


def approve_all(data):
    count = 0
    for item in data["items"]:
        if item["review_status"] == "pending":
            item["review_status"] = "approved"
            count += 1
    save(data)
    print(f"✅ 已批量通过 {count} 条标准")


def export_csv(data):
    approved = [x for x in data["items"] if x["review_status"] == "approved"]
    if not approved:
        print("⚠️  没有已通过的条目")
        return

    output = BASE_DIR / "approved_standards.csv"
    with open(output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "category", "keyword", "phase", "std_type", "code", "title",
            "status", "detail_url", "crawled_at"
        ])
        writer.writeheader()
        for item in approved:
            writer.writerow({k: item.get(k, "") for k in writer.fieldnames})

    print(f"📄 已导出 {len(approved)} 条到 {output}")


def main():
    parser = argparse.ArgumentParser(description="零碳能源知识库审核工具")
    parser.add_argument("--show", action="store_true", help="查看待审列表")
    parser.add_argument("--keyword", help="筛选关键词")
    parser.add_argument("--approve-all", action="store_true", help="批量通过所有待审条目")
    parser.add_argument("--export", action="store_true", help="导出已通过条目为CSV")
    args = parser.parse_args()

    data = load()
    if data is None:
        return

    if args.show:
        show_summary(data, args.keyword)
    elif args.approve_all:
        approve_all(data)
    elif args.export:
        export_csv(data)
    else:
        parser.print_help()
        # 默认显示汇总
        show_summary(data)


if __name__ == "__main__":
    main()
