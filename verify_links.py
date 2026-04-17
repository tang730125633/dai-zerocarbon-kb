#!/usr/bin/env python3
"""
零碳能源知识库 - 链接有效性验证
检查 review_index.json 中每条标准的 detail_url 是否真实可访问。

用法：
  python3 verify_links.py              # 验证所有未验证的链接
  python3 verify_links.py --re-verify  # 重新验证所有链接（包括已验证的）
  python3 verify_links.py --report     # 只输出验证报告，不执行验证
"""

import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
REVIEW_FILE = BASE_DIR / "review_index.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://std.samr.gov.cn/",
}


def load():
    if not REVIEW_FILE.exists():
        print("❌ review_index.json 不存在，请先运行 crawler.py")
        return None
    with open(REVIEW_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    data["updated_at"] = datetime.now().isoformat()
    with open(REVIEW_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_url(url, timeout=10):
    """
    检查 URL 是否有效。
    返回：(is_valid: bool, status_code: int, note: str)
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        code = resp.status_code
        if code == 200:
            # 进一步确认：页面是否包含标准信息（避免 200 但内容是错误页）
            text = resp.text
            if "404" in text[:500] or "未找到" in text[:500] or "不存在" in text[:500]:
                return False, code, "200但内容为404"
            if len(text) < 500:
                return False, code, "200但内容过短"
            return True, code, "OK"
        elif code == 302 or code == 301:
            return True, code, "重定向"
        else:
            return False, code, f"HTTP {code}"
    except requests.exceptions.Timeout:
        return False, 0, "超时"
    except requests.exceptions.ConnectionError:
        return False, 0, "连接失败"
    except Exception as e:
        return False, 0, str(e)[:50]


def verify_all(data, re_verify=False):
    items = data["items"]
    to_verify = [
        item for item in items
        if re_verify or item.get("link_valid") is None
    ]

    print(f"\n🔍 待验证链接：{len(to_verify)} 条 (共 {len(items)} 条)")
    if not to_verify:
        print("✅ 所有链接已验证")
        return

    valid = 0
    invalid = 0
    for i, item in enumerate(to_verify, 1):
        url = item.get("detail_url", "")
        if not url:
            item["link_valid"] = False
            item["link_note"] = "无URL"
            invalid += 1
            continue

        is_valid, status_code, note = check_url(url)
        item["link_valid"] = is_valid
        item["link_status_code"] = status_code
        item["link_note"] = note
        item["link_verified_at"] = datetime.now().isoformat()

        status_icon = "✅" if is_valid else "❌"
        print(f"  [{i}/{len(to_verify)}] {status_icon} {item['code'][:20]:20} {note} ({status_code})")
        print(f"      {url}")

        if is_valid:
            valid += 1
        else:
            invalid += 1

        # 每5条保存一次，防止中途中断丢失数据
        if i % 5 == 0:
            save(data)

        time.sleep(0.8)  # 礼貌性延迟

    save(data)
    print(f"\n📊 验证完成：有效 {valid} | 无效 {invalid} | 共 {len(to_verify)} 条")


def print_report(data):
    items = data["items"]
    verified = [x for x in items if x.get("link_valid") is not None]
    valid = [x for x in verified if x.get("link_valid") is True]
    invalid = [x for x in verified if x.get("link_valid") is False]
    unverified = [x for x in items if x.get("link_valid") is None]

    print(f"\n{'='*60}")
    print(f"🔗 链接验证报告")
    print(f"{'='*60}")
    print(f"总计：{len(items)} 条")
    print(f"✅ 有效：{len(valid)} 条")
    print(f"❌ 无效：{len(invalid)} 条")
    print(f"⏳ 未验证：{len(unverified)} 条")

    if invalid:
        print(f"\n--- 无效链接列表 ---")
        for item in invalid:
            print(f"  [{item.get('link_note', '?')}] {item['code']} {item['title'][:40]}")
            print(f"    {item.get('detail_url', '')}")

    if unverified:
        print(f"\n--- 未验证（{len(unverified)}条，运行 verify_links.py 验证）---")


def main():
    parser = argparse.ArgumentParser(description="零碳能源知识库链接验证工具")
    parser.add_argument("--re-verify", action="store_true", help="重新验证所有链接")
    parser.add_argument("--report", action="store_true", help="只输出报告")
    args = parser.parse_args()

    data = load()
    if data is None:
        return

    if args.report:
        print_report(data)
    else:
        verify_all(data, re_verify=args.re_verify)
        print_report(data)


if __name__ == "__main__":
    main()
