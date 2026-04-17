# 戴总零碳能源标准知识库

> 为戴总企业搭建的零碳能源领域**标准库自动采集、查重、导入**体系。

---

## 📊 当前数据

- **总量**：2509 条国家/行业/地方标准
- **覆盖**：发电 / 输电 / 变电 / 配电 / 用电 / 电力交易
- **数据源**：
  - [`std.samr.gov.cn`](https://std.samr.gov.cn) — 国标/行标（主力）
  - `bzfxw.com` — PDF 下载（需 VPN）
- **最后更新**：2026-04-03

### 分布

| 一级分类 | 条数 |
|---------|-----|
| 发电 | 726 |
| 用电 | 693 |
| 输电 | 545 |
| 变电 | 367 |
| 配电 | 124 |
| 电力交易 | 54 |

### 编号前缀

| 类型 | 前缀 | 数量 |
|------|------|------|
| 国标 | GB / GB/T | 774 |
| 电力行标 | DL / DL/T | 731 |
| 能源行标 | NB / NB/T | 290 |
| 地方标准 | DB* | ~170 |

---

## 🗂️ 仓库结构

```
dai-zerocarbon-kb/
├── README.md                  本文件
├── AGENTS.md                  AI 接手指南（原 _AI接手指南.md）
├── crawler.py                 爬虫（std.samr.gov.cn）
├── verify_links.py            链接有效性验证
├── review.py                  审核工具
├── review_index.json          ← 2509 条完整索引（核心数据）
├── 发电/ 输电/ 变电/ 配电/ 用电/ 电力交易/   目录结构占位（按分类归档）
└── [未来] normalize_code.py   编号规范化（查重前置）
└── [未来] dedup.py            查重主逻辑
└── [未来] reference_lists/    戴总侧参照清单（用于查重）
```

---

## 🤖 AI Agent 如何使用

### 本仓库用于
- 小夏（Tang MacBook Hermes）— 爬取、查重、维护索引
- 小琳（戴总 Mac mini OpenClaw）— 从审核通过的条目导入小程序

### 工作流
```
Step 1  小夏 crawler.py      爬取新标准
Step 2  小夏 verify_links    验证 detail_url
Step 3  小夏 dedup.py        和戴总现有清单查重
Step 4  戴总审核（飞书群/小程序）
Step 5  小琳 import.py       导入戴总小程序
```

### 知识库的更大上下文
本仓库是"戴总企业服务三大系统"的第二大系统。参见 Tang 的 AI 记忆仓库 [`llm-wiki-agent-memory`](https://github.com/tang730125633/llm-wiki-agent-memory)。

---

## 🚀 快速上手（新机器部署）

```bash
git clone https://github.com/tang730125633/dai-zerocarbon-kb.git
cd dai-zerocarbon-kb
pip install -r requirements.txt  # requests, beautifulsoup4

# 爬取（示例：抽水蓄能）
python3 crawler.py --keyword 抽水蓄能 --category 发电

# 验证链接
python3 verify_links.py

# 审核
python3 review.py --show
```

---

## 🔒 安全边界

| 可入仓库 | 不可入仓库 |
|----------|-----------|
| ✅ 爬虫代码、查重逻辑 | ❌ 戴总小程序 API Key / Token |
| ✅ 公开标准的编号、标题 | ❌ 戴总内部运营数据 |
| ✅ 分类目录结构 | ❌ 用户凭据、密码 |

凭据一律放 `.env`（已 `.gitignore`）。

---

## 📋 待解问题

- [ ] 戴总小程序的导入 API（戴总侧即将提供）
- [ ] PDF 下载的 VPN 方案（`bzfxw.com`）
- [ ] 戴总现有 PDF 清单的比对（清单即将提供）
- [ ] 编号规范化算法（处理 GB/T 空格/全角/斜杠等变体）

---

## 🔗 相关

- 主维护者：Tang（小夏 Hermes）
- 源数据：[std.samr.gov.cn](https://std.samr.gov.cn)
- AI 记忆仓库：[llm-wiki-agent-memory](https://github.com/tang730125633/llm-wiki-agent-memory)

---

*基于 Karpathy LLM Wiki 模式维护的自动化知识库项目*
