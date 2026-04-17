# 零碳能源知识库 · AI 接手指南

> 任何 AI 读完这份文档，就能立刻参与工作。

---

## 项目是什么

为"戴总"搭建的**零碳能源领域标准知识库**。
目标：把国家标准、行业标准、企业标准按工程环节自动分类，导入 OpenClaw 知识库供检索。

---

## 目录结构

```
零碳能源知识库/
├── 发电/输电/变电/配电/用电/     ← 656个分类目录（已建好）
│   └── {子项}/{环节}/{标准类型}/  ← 例：发电/抽水蓄能/设计/国家标准/
│
├── crawler.py          ← 爬虫：从 samr.gov.cn 抓取标准索引
├── review.py           ← 审核工具：查看/批准/导出爬取结果
├── verify_links.py     ← 链接验证：检查 detail URL 是否真实有效
├── review_index.json   ← 核心数据文件（所有爬取结果 + 审核状态）
├── approved_standards.csv  ← 审核通过后导出，供 OpenClaw 导入
└── _AI接手指南.md      ← 本文件
```

---

## 数据来源

| 网站 | 用途 | 是否需要 VPN |
|------|------|-------------|
| https://std.samr.gov.cn | 国家/行业标准检索（主力） | 否 |
| https://www.bzfxw.com | 标准 PDF 下载（含无 VIP 直接下载） | 是 |

### samr.gov.cn 接口规则

**搜索接口：**
```
GET https://std.samr.gov.cn/search/stdPage?q={关键词}&tid=&pageNo={页码}
返回：HTML，每页10条，带分页信息
```

**详情页 URL 规则（从搜索结果中的 tid/pid 属性构造）：**
```
行业标准 (tid=BV_HB): https://std.samr.gov.cn/hb/search/stdHBDetailed?id={pid}
地方标准 (tid=BV_DB): https://std.samr.gov.cn/db/search/stdDBDetailed?id={pid}
国家标准 (其他):      https://std.samr.gov.cn/gb/search/gbDetailed?id={pid}
```

---

## 知识库分类逻辑

### 一级目录（5个）
`发电` · `输电` · `变电` · `配电` · `用电`

### 二级目录（子项关键词）
```
发电: 抽水蓄能、风力发电、光伏发电、分布式发电、水力发电、核能发电、生物质发电、地热发电
输电: 架空线路、电缆线路、特高压输电、直流输电、柔性输电
变电: 变电站、换流站、GIS变电站、智能变电站
配电: 配电网、开关柜、箱式变电站、配电自动化
用电: 用电安全、节能管理、需求侧管理、电能质量、储能系统
```

### 三级目录（工程环节，固定6个）
`勘测` · `设计` · `造价` · `施工` · `验收` · `运维`

### 四级目录（标准类型，固定3个）
`国家标准` · `行业标准` · `企业标准`

---

## review_index.json 数据结构

每条标准的字段：
```json
{
  "code": "NB/T 35071-2025",
  "title": "抽水蓄能电站水能规划设计规范",
  "status": "即将实施",
  "std_type": "行业标准",
  "std_type_raw": "行业标准",
  "detail_url": "https://std.samr.gov.cn/hb/search/stdHBDetailed?id=...",
  "tid": "BV_HB",
  "pid": "4D49CE8CA2138559E06397BE0A0AA2EE",
  "category": "发电",
  "keyword": "抽水蓄能",
  "phase": "设计",
  "review_status": "pending",   ← pending / approved / rejected
  "review_note": "",
  "link_valid": null,            ← null=未验证, true=有效, false=无效
  "crawled_at": "2026-04-02T..."
}
```

---

## 当前工作流

```
Step 1  crawler.py --all       爬取全部关键词的标准索引
Step 2  verify_links.py        验证所有 detail_url 是否真实可访问
Step 3  review.py --show       展示给戴总看，人工确认分类是否准确
Step 4  review.py --approve-all 或逐条审核
Step 5  review.py --export     导出 CSV → 导入 OpenClaw
```

---

## AI 可以做的任务

### Task A：验证链接有效性
```bash
python3 verify_links.py
```
检查 review_index.json 中每条标准的 detail_url，标记 `link_valid: true/false`。

### Task B：补充爬取某个关键词
```bash
python3 crawler.py --keyword 风力发电 --category 发电
```

### Task C：改进环节分类
当前用关键词猜测 `phase` 字段（勘测/设计/造价/施工/验收/运维）。
可以读取 review_index.json，对 phase 判断有误的条目提出修正建议。

**判断依据（标准名称中常见词）：**
- 勘测：勘测、勘察、测量、地质、地形、水文、勘探
- 设计：设计、规划、规范、导则、技术条件、技术规程
- 造价：造价、定额、费用、概算、预算、计量
- 施工：施工、安装、建设、组立、敷设
- 验收：验收、检测、试验、调试、竣工
- 运维：运维、运行、维护、检修、巡视、管理

### Task D：检查重复条目
review_index.json 中可能存在不同关键词搜到同一标准（code相同）的情况，可以去重。

---

## 注意事项

- samr.gov.cn 不需要登录，但请求间隔 ≥ 1秒，避免被封
- bzfxw.com 需要 VPN 才能访问
- 企业标准（Q/ 开头）在 samr.gov.cn 上查不到，需要单独处理
- `review_status` 只有人工确认后才能改为 approved，不要自动批准
