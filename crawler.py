#!/usr/bin/env python3
"""
零碳能源知识库 - 标准爬虫
数据来源：https://std.samr.gov.cn
用法：python3 crawler.py [--keyword 抽水蓄能] [--category 发电] [--phase 设计]
"""

import requests
import json
import time
import re
import argparse
import os
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
REVIEW_FILE = BASE_DIR / "review_index.json"

# 知识库结构定义
# 格式：{"大类": ["关键词"]}，关键词用于搜索，可以是宽泛词以获取更多结果
STRUCTURE = {
    "发电": [
        "抽水蓄能", "风力发电", "光伏发电", "分布式发电",
        "水力发电", "核电站",
        "生物质发电", "地热能发电",
        "余热发电", "余热利用发电",
        "海洋能发电", "潮汐发电", "波浪能",   # 新增：海洋能
        "氢能发电", "燃料电池发电", "氢燃料电池",  # 新增：氢能
    ],
    "输电": [
        "架空输电线路", "电缆线路",
        "特高压", "直流输电", "柔性直流",
        "气体绝缘输电线路", "GIL输电",        # 新增：GIL
        "柔性直流输电",                        # 新增：更精准的柔直
    ],
    "变电": [
        "变电站", "换流站",
        "气体绝缘金属封闭",              # GIS变电站 → 气体绝缘（更宽泛）
        "智能变电站",
        "预装式变电站", "箱式变",        # 箱式变电站 → 两个宽泛词
    ],
    "配电": [
        "配电网", "高压开关柜", "中压开关柜",  # 开关柜拆成两个
        "箱式变电站", "配电自动化",
    ],
    "用电": [
        "用电安全", "节能管理",
        "电力需求侧", "负荷管理",
        "电能质量",
        "电化学储能", "储能电站",
        "电能替代", "以电代煤", "以电代气",   # 新增：电能替代
        "虚拟电厂", "聚合负荷",               # 新增：虚拟电厂
        "综合能源服务", "多能互补",            # 新增：综合能源服务
        "数据中心供电", "数据中心电气",        # 新增：数据中心
    ],
    "电力交易": [
        "电力市场", "电力交易", "售电",
        "碳交易", "绿电交易", "电力现货",
    ],
}

PHASES = ["勘测", "设计", "造价", "施工", "验收", "运维"]

# samr.gov.cn URL 规则
SAMR_SEARCH = "https://std.samr.gov.cn/search/stdPage"
SAMR_DETAIL = {
    "BV_HB": "https://std.samr.gov.cn/hb/search/stdHBDetailed?id={pid}",
    "BV_DB": "https://std.samr.gov.cn/db/search/stdDBDetailed?id={pid}",
    "DEFAULT": "https://std.samr.gov.cn/gb/search/gbDetailed?id={pid}",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://std.samr.gov.cn/",
}


def get_detail_url(tid, pid):
    tmpl = SAMR_DETAIL.get(tid, SAMR_DETAIL["DEFAULT"])
    return tmpl.format(pid=pid)


def detect_std_type(code, industry):
    """根据标准编号和行业判断标准类型"""
    code = code.strip()
    if code.startswith("GB"):
        return "国家标准"
    elif code.startswith("Q/"):
        return "企业标准"
    elif re.match(r'^(DL|NB|SL|HJ|JB|YD|JGJ|CJJ|HG|SH|TB|MH|QB)', code):
        return "行业标准"
    else:
        return "国家标准"  # 默认归国家标准


def guess_phase(title):
    """根据标准名称猜测所属环节"""
    title = title.lower()
    phase_keywords = {
        "勘测": ["勘测", "勘察", "测量", "地质", "地形", "水文", "勘探"],
        "设计": ["设计", "规划", "规范", "导则", "技术条件", "技术规程"],
        "造价": ["造价", "定额", "费用", "概算", "预算", "计量"],
        "施工": ["施工", "安装", "建设", "组立", "敷设"],
        "验收": ["验收", "检测", "试验", "调试", "竣工"],
        "运维": ["运维", "运行", "维护", "检修", "巡视", "管理"],
    }
    for phase, keywords in phase_keywords.items():
        if any(kw in title for kw in keywords):
            return phase
    return "设计"  # 默认归设计


def search_standards(keyword, page=1):
    """搜索标准，返回当页结果列表"""
    params = {"q": keyword, "tid": "", "pageNo": page}
    try:
        resp = requests.get(SAMR_SEARCH, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 总数
        total_match = re.search(r'找到相关结果约.*?(\d+)', resp.text)
        total = int(total_match.group(1)) if total_match else 0

        items = []
        for post in soup.find_all("div", class_="post"):
            link = post.find("a", href=True)
            if not link:
                continue

            tid = link.get("tid", "")
            pid = link.get("pid", "")
            code_el = post.find(class_="en-code")
            code = code_el.get_text(strip=True) if code_el else ""
            title = link.get_text(strip=True).replace(code, "").strip()
            status_el = post.find(class_="s-status")
            status = status_el.get_text(strip=True) if status_el else ""

            # 标准类型
            type_el = post.find(class_="line11")
            std_type_raw = type_el.get_text(strip=True) if type_el else ""

            if not code or not pid:
                continue

            items.append({
                "code": code,
                "title": title,
                "status": status,
                "std_type_raw": std_type_raw,
                "std_type": detect_std_type(code, std_type_raw),
                "detail_url": get_detail_url(tid, pid),
                "tid": tid,
                "pid": pid,
            })

        return items, total

    except Exception as e:
        print(f"  ⚠️  搜索失败: {e}")
        return [], 0


def crawl_keyword(keyword, category, max_pages=10):
    """爬取某个关键词的所有标准"""
    print(f"\n🔍 爬取: {category} > {keyword}")
    all_items = []
    page = 1

    while page <= max_pages:
        items, total = search_standards(keyword, page)
        if not items:
            break
        all_items.extend(items)
        total_pages = (total + 9) // 10
        print(f"  第{page}/{total_pages}页，本页{len(items)}条，共{total}条")
        if page >= total_pages:
            break
        page += 1
        time.sleep(1)  # 礼貌性延迟

    # 为每条标准猜测所属环节
    results = []
    for item in all_items:
        phase = guess_phase(item["title"])
        results.append({
            **item,
            "category": category,
            "keyword": keyword,
            "phase": phase,
            "review_status": "pending",  # pending / approved / rejected
            "review_note": "",
            "crawled_at": datetime.now().isoformat(),
        })

    print(f"  ✅ 共获取 {len(results)} 条标准")
    return results


def load_review_index():
    if REVIEW_FILE.exists():
        with open(REVIEW_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"updated_at": "", "stats": {}, "items": []}


def save_review_index(data):
    data["updated_at"] = datetime.now().isoformat()
    # 统计
    items = data["items"]
    data["stats"] = {
        "total": len(items),
        "pending": sum(1 for x in items if x["review_status"] == "pending"),
        "approved": sum(1 for x in items if x["review_status"] == "approved"),
        "rejected": sum(1 for x in items if x["review_status"] == "rejected"),
        "by_category": {},
    }
    for item in items:
        cat = item.get("category", "unknown")
        data["stats"]["by_category"].setdefault(cat, 0)
        data["stats"]["by_category"][cat] += 1

    with open(REVIEW_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存到 {REVIEW_FILE}")
    print(f"   总计: {data['stats']['total']} 条")
    print(f"   待审: {data['stats']['pending']} | 通过: {data['stats']['approved']} | 拒绝: {data['stats']['rejected']}")


def main():
    parser = argparse.ArgumentParser(description="零碳能源知识库标准爬虫")
    parser.add_argument("--keyword", help="指定关键词（如：抽水蓄能）")
    parser.add_argument("--category", help="指定大类（如：发电）")
    parser.add_argument("--all", action="store_true", help="爬取全部关键词")
    parser.add_argument("--max-pages", type=int, default=10, help="每个关键词最多爬取页数")
    args = parser.parse_args()

    index = load_review_index()
    existing_keys = {(x["keyword"], x["code"]) for x in index["items"]}

    new_items = []

    if args.all:
        # 爬取全部
        for category, keywords in STRUCTURE.items():
            for keyword in keywords:
                items = crawl_keyword(keyword, category, args.max_pages)
                for item in items:
                    if (item["keyword"], item["code"]) not in existing_keys:
                        new_items.append(item)

    elif args.keyword:
        # 爬取指定关键词
        category = args.category or "未分类"
        # 自动检测大类
        if not args.category:
            for cat, kws in STRUCTURE.items():
                if args.keyword in kws:
                    category = cat
                    break
        items = crawl_keyword(args.keyword, category, args.max_pages)
        for item in items:
            if (item["keyword"], item["code"]) not in existing_keys:
                new_items.append(item)

    else:
        parser.print_help()
        return

    if new_items:
        index["items"].extend(new_items)
        save_review_index(index)
        print(f"\n🆕 新增 {len(new_items)} 条标准到审核列表")
    else:
        print("\n⚠️  没有新增条目（可能已全部爬取过）")


if __name__ == "__main__":
    main()
