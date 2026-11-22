# B题文件结构说明

整理日期：2026-11-22。采用“零改脚本”方案：四题目录、`论文图表/`、论文源稿和构建脚本保留在根目录，保证原有命令可直接运行。

## 目录一览

| 位置 | 内容 |
|---|---|
| `00_赛题与规范/` | 赛题 PDF、Word 模版、承诺书、论文格式规范、提交流程；`图表模板/` 为 5 张样式参考图 |
| `01_论文/` | 最终提交版 `数维杯B题_中文初稿_11图_最新.docx` |
| `01_论文/备查/` | 全图版 `数维杯B题_中文初稿.docx`、`数维杯B题_中文初稿_11图预览.docx`、`update_toc.ps1` |
| `01_论文/过程文档/` | AI 交接文档、修改汇总、两份复核意见、`反馈截图/` |
| `第一题/`～`第四题/` | 各题 `code/`、`results/`、`figures/` 及三份文档（未改动） |
| `论文图表/` | 论文正文引用的 `fig4-*`、`fig0_*` 图表及绘图脚本 |
| `99_归档/` | 备份、临时测试、旧版预览、日志、调试脚本；明细见 `整理清单_20261122.md` |

## 根目录保留文件

| 文件 | 用途 |
|---|---|
| `数维杯B题_中文初稿.md` | 论文中文源稿（摘要、正文、图号标记） |
| `numbers.md` | 正文数字与 JSON 数据源的逐项对照 |
| `params.csv` / `params_table.md` | 场地、建筑、车辆、告警参数 |
| `build_docx_paper_cn.py` | Markdown → Word（表格、图注、页码、目录域） |
| `build_numbers.py` | 由各题 `results/*.json` 重建 `numbers.md` |
| `check_consistency.py` | 论文 ↔ `numbers.md` ↔ JSON 数值一致性校验 |
| `_tmp_make11.py` | 从论文源稿生成 11 图版中间稿 `_tmp_md_11fig.md` |
| `_tmp_md_11fig.md` | 11 图版 Word 的构建输入 |

## 常用命令（均在 `B题/` 下执行）

```bash
# 数值一致性检查
python -I check_consistency.py

# 由 JSON 重建 numbers.md
python -I build_numbers.py

# 生成 11 图版中间稿
python -I _tmp_make11.py

# 构建 11 图版 Word（输出到 01_论文/）
PAPER_MD=_tmp_md_11fig.md \
PAPER_OUT=01_论文/数维杯B题_中文初稿_11图_最新.docx \
PAPER_APPENDIX_START=22 PAPER_BODY_PAGES=21 \
python -I build_docx_paper_cn.py
```

## 注意事项

- 根目录的源稿、`numbers.md`、`params.*`、`论文图表/` 和四题目录被脚本按相对路径引用，移动后需同步修改脚本。
- `01_论文/备查/update_toc.ps1` 使用脚本所在目录，打开同目录的 `数维杯B题_中文初稿.docx` 并更新目录/域；更新最终版时请先改脚本中的文件名。
- `99_归档/` 中的 `.bak`、`_tmp_p2_*`、日志和调试脚本仅作追溯，不参与构建。
