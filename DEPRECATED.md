# ⚠️ 已废弃 / DEPRECATED

**本仓库于 2026-04-17 合并到 [dai-knowledge-base](https://github.com/tang730125633/dai-knowledge-base)**

## 为什么废弃

本仓库只承载了 samr.gov.cn 的 2509 条标准索引。但实际上 Tang 更早（2026-04-01）已建立了更完整的主仓库 `dai-knowledge-base`，它包含：

- bzfxw.com 的 PDF 下载链接数据
- 完整的 4 层目录结构（大类/子品类/生命周期/标准来源）
- 1140 个 `标准索引.md` 文件骨架
- 更丰富的爬虫生态（bulk/bzfxw/classify/generate_indexes 等 8 个脚本）

保留本仓库的数据**仅覆盖了主仓库能力的一个片段**，继续双头维护会造成分歧。

## 迁移目标

所有内容已合并到 [dai-knowledge-base](https://github.com/tang730125633/dai-knowledge-base)：

| 原本仓库文件 | 新位置 |
|-------------|--------|
| `review_index.json` | `_crawl_data/samr_review_index.json` |
| `crawler.py` | `samr_crawler.py` |
| `verify_links.py` | `samr_verify_links.py` |
| `review.py` | `samr_review.py` |
| `AGENTS.md` | 已合并到主仓库文档 |

详见主仓库的 [`SAMR-DATA-MERGE-NOTE.md`](https://github.com/tang730125633/dai-knowledge-base/blob/main/SAMR-DATA-MERGE-NOTE.md)。

## 历史意义

本仓库是 2026-04-17 Tang 准备部署戴总 Mac mini 时的**临时承载**，见证了"双头维护到合并"的过程。归档保留作为历史记录，不再接收提交。
