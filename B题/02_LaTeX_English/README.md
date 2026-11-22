# 数维杯 B 题 · 英文 LaTeX 稿

本目录是英文论文的 LaTeX 版本，基于赛事官方 `swmcmthesis` 模板。

## 目录结构

```
02_LaTeX_English/
├── main.tex                  # 主文件：模板配置、摘要页、章节装配、页眉/编号
├── swmcmthesis.cls           # 官方模板类文件
├── swmcmthesis.cfg           # 官方模板配置
├── sections/
│   ├── 01_intro_analysis.tex # 第 1–2 章
│   ├── 02_symbols.tex        # 第 3 章
│   ├── 03_model_q1q2.tex     # 第 4.1–4.3 节（问题 1、2）
│   ├── 04_model_q3q4.tex     # 第 4.4–4.5 节（问题 3、4）
│   ├── 05_results_conclusion.tex # 第 5–8 章 + 参考文献
│   └── 06_appendix.tex       # 附录 A–C
├── figures/                  # 12 张图（PNG，图内已是英文标注）
└── compile.bat               # Windows 双击编译
```

## 编译

推荐 **pdfLaTeX**（模板按 pdfLaTeX 设计）：

```bat
pdflatex main
pdflatex main
```

或直接双击 `compile.bat`。第二遍是必要的，用于稳定目录和页码。

## 队伍编号

- `main.tex` 中的 `\baominghao{SWBMCM2611718}` 已填入实际队号，摘要页与页眉会自动使用。
- pdfLaTeX 不能直接编译中文占位符，因此 LaTeX 版必须使用 ASCII 队号，不要改回 `<队伍号>`。
- 附录 B 的程序路径使用 ASCII 别名（`Q1/`、`Q2/`、`Q3/`、`Q4/`）以兼容 pdfLaTeX；实际源码目录仍是中文名。

## 页码与页眉

- 摘要页、目录页：按模板不设页眉。
- 正文：`Team # 队号` + `Page X of 25`，正文从第 1 页重新编号。
- 附录：`Appendix Page A/B/C`，单独编号，不计入正文 25 页限制。

## 说明

- 本机当前未检测到 TeX 引擎，因此尚未生成 PDF；安装 MiKTeX/TeX Live 后按上述命令编译即可。
- 图片直接复用 `../论文图表/` 中已带英文标注的 PNG；如需矢量图，可把同目录 SVG 转成 PDF 后替换 `figures/` 中的文件。
