---
name: auto-research
description: |
  一站式学术研究工作流：论文检索与阅读(arXiv + Zotero)、文献综述写作(Google Docs)、
  学术插图生成(PaperBanana)、架构图绘制(draw.io)、演示文稿制作(python-pptx / Pencil)。
  整合 paper-research、google-docs、paper-banana、drawio、zotero-mcp、pptx 六大子技能。
version: 1.0.0
user-invocable: true
---

# Auto Research Skills

一站式学术研究工作流，覆盖从论文检索到最终演示的完整链路。

## 子技能一览

| 子技能 | 用途 | 核心工具 |
|--------|------|----------|
| **paper-research** | arXiv 检索、PDF 提取、文献综述生成 | Python 脚本 |
| **zotero** | 文献库管理、注释提取、引用搜索 | zotero-mcp |
| **google-docs** | 读写 Google Docs、Drive 文件管理 | Ruby 脚本 |
| **paper-banana** | 学术插图生成（框架图、统计图） | PaperBanana AI |
| **drawio** | 架构图、流程图、ER 图 | draw.io XML |
| **pptx** | 演示文稿生成与编辑 | python-pptx |

---

## 快速开始：典型研究工作流

```
1. 检索论文    →  paper-research (arXiv) + zotero (已有文献库)
2. 阅读与笔记  →  zotero (PDF 注释提取) + paper-research (文本提取)
3. 写文献综述  →  google-docs (直接在 Google Doc 中编辑)
4. 画学术插图  →  paper-banana (AI 生成框架图/统计图)
5. 画架构图    →  drawio (生成 .drawio 或导出 PNG/SVG)
6. 做演示文稿  →  pptx (python-pptx 生成 .pptx)
```

---

## 1. Paper Research（论文检索与综述）

详见 `skills/paper-research/SKILL.md`

### 核心命令

```bash
# 搜索 arXiv
python3 skills/paper-research/scripts/arxiv_survey.py \
  --terms "egocentric video" "action recognition" \
  --max-results 100 --download-pdfs --pdf-dir ./pdfs --out ./arxiv.jsonl

# 提取 PDF 文本
python3 skills/paper-research/scripts/pdf_extract.py \
  --pdf-dir ./pdfs --out-dir ./texts --sections

# 获取 BibTeX
python3 skills/paper-research/scripts/arxiv_bibtex.py \
  --from-jsonl ./arxiv.jsonl --out ./refs.bib

# 生成结构化报告
python3 skills/paper-research/scripts/generate_report.py \
  --jsonl ./arxiv.jsonl --out ./REPORT.md
```

### 工作流模式

- **A) 文献综述计划**：生成 REPORT.md → 构建综述大纲 → 填充内容
- **B) 可复现性优先筛选**：按代码可用性、协议完整性排序
- **C) 实验设计**：假设 → 任务 → 指标 → 探测实验

---

## 2. Zotero（文献库管理）

详见 `skills/zotero/README.md`

### 前置配置

```bash
# 安装 zotero-mcp
pip install zotero-mcp

# 添加到 Claude Code（本地模式）
claude mcp add-json "zotero" '{"command":"zotero-mcp","env":{"ZOTERO_LOCAL":"true"}}'
```

需要 Zotero 桌面版正在运行，且安装了 Better BibTeX 插件。

### 核心能力

- **搜索文献库**：按关键词、作者、标签搜索已收藏论文
- **提取 PDF 注释**：获取高亮、笔记、批注
- **语义搜索**：基于向量的相似度搜索（需配置 embedding）
- **获取元数据**：标题、作者、摘要、标签、收藏夹信息
- **引用导出**：导出 BibTeX、CSL-JSON 等格式

### 典型用法

通过 MCP 工具直接调用（Claude Code 会自动识别）：

```
"搜索我 Zotero 里关于 egocentric video 的论文"
"提取这篇论文的 PDF 注释"
"列出 'ACM MM 2026' 收藏夹里的所有论文"
```

---

## 3. Google Docs（文档读写）

详见 `skills/google-docs/SKILL.md`

### 前置配置

1. Google Cloud 项目启用 Docs API + Drive API
2. 创建 OAuth 桌面应用凭证
3. 保存为 `~/.claude/.google/client_secret.json`
4. 首次运行时完成 OAuth 授权

### 核心命令

```bash
DOCS=~/.claude/skills/google-docs/scripts/docs_manager.rb
DRIVE=~/.claude/skills/google-docs/scripts/drive_manager.rb

# 读取文档
$DOCS read <document_id>

# 获取文档结构（标题层级）
$DOCS structure <document_id>

# 从 Markdown 创建文档
echo '{"title": "论文草稿", "markdown": "# Title\n\n## Abstract\n\nContent..."}' | $DOCS create

# 插入文本
echo '{"document_id": "<id>", "text": "新增内容", "index": 1}' | $DOCS insert

# 查找替换
echo '{"document_id": "<id>", "find": "旧文本", "replace": "新文本"}' | $DOCS find-replace

# 追加 Markdown 内容
echo '{"document_id": "<id>", "markdown": "## New Section\n\nContent..."}' | $DOCS append

# 搜索 Drive 文件
$DRIVE search --query "name contains 'paper'"

# 分享文件
echo '{"file_id": "<id>", "email": "collaborator@gmail.com", "role": "writer"}' | $DRIVE share
```

### 从文档 URL 提取 ID

Google Docs URL 格式：`https://docs.google.com/document/d/<DOCUMENT_ID>/edit`

提取 `/d/` 和 `/edit` 之间的部分即为 document_id。

---

## 4. Paper Banana（学术插图生成）

详见 `skills/paper-banana/SKILL.md`

### 前置安装

```bash
# 克隆 PaperBanana 项目
git clone https://github.com/paperbanana/PaperBanana.git ~/PaperBanana
cd ~/PaperBanana && pip install -r requirements.txt

# 配置模型（编辑 configs/model_config.yaml）
```

### 核心命令

```bash
SCRIPT=~/.claude/skills/auto-research/skills/paper-banana/scripts/generate_figure.py

# 从方法描述生成框架图
python3 $SCRIPT \
  --content @method_section.md \
  --caption "Figure 1: System architecture" \
  --output ./fig1.png

# 生成统计图
python3 $SCRIPT \
  --content "实验结果数据..." \
  --caption "Figure 2: Performance comparison" \
  --output ./fig2.png \
  --task plot

# 高质量模式
python3 $SCRIPT \
  --content @method.md \
  --caption "Figure 3: Pipeline" \
  --output ./fig3.png \
  --exp-mode demo_full --critic-rounds 5
```

### 管线模式

| 模式 | 流程 | 适用场景 |
|------|------|----------|
| `demo_planner_critic` | Planner → Visualizer → Critic × N | 快速生成，推荐默认 |
| `demo_full` | Retriever → Planner → Stylist → Visualizer → Critic × N | 更精美，含风格优化 |

---

## 5. Draw.io（架构图绘制）

详见 `skills/drawio/SKILL.md`

### 基本流程

1. 生成 mxGraphModel XML
2. 写入 `.drawio` 文件
3. （可选）导出为 PNG/SVG/PDF

### XML 基础结构

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- 图形元素放这里，parent="1" -->
  </root>
</mxGraphModel>
```

### 导出命令

```bash
# macOS draw.io CLI 路径
DRAWIO="/Applications/draw.io.app/Contents/MacOS/draw.io"

# 导出为 PNG（嵌入 XML，可再次编辑）
$DRAWIO -x -f png -e -b 10 -o output.drawio.png input.drawio

# 导出为 SVG
$DRAWIO -x -f svg -e -o output.drawio.svg input.drawio

# 导出为 PDF
$DRAWIO -x -f pdf -e -o output.drawio.pdf input.drawio
```

### 常用样式

| 元素 | style 属性 |
|------|-----------|
| 圆角矩形 | `rounded=1;whiteSpace=wrap;` |
| 菱形（判断） | `rhombus;whiteSpace=wrap;` |
| 圆柱体（数据库） | `shape=cylinder3;whiteSpace=wrap;` |
| 正交连线 | `edgeStyle=orthogonalEdgeStyle;` |
| 虚线 | `dashed=1;` |
| 泳道 | `swimlane;` |

### 命名规范

- 文件名用小写+连字符：`login-flow.drawio`
- 导出用双扩展名：`login-flow.drawio.png`（保留可编辑性）

---

## 6. PPTX（演示文稿）

详见 `skills/pptx/README.md`

### 前置安装

```bash
pip install python-pptx
```

### 使用方式

通过 Python 脚本生成 .pptx 文件：

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

prs = Presentation()

# 标题幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "ACM MM 2026"
slide.placeholders[1].text = "Agentic VLM in Egocross"

# 内容幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Motivation"
body = slide.placeholders[1]
body.text = "First point"
p = body.text_frame.add_paragraph()
p.text = "Second point"
p.level = 1

# 插入图片
slide = prs.slides.add_slide(prs.slide_layouts[5])  # 空白布局
slide.shapes.add_picture("arch.png", Inches(1), Inches(1), width=Inches(8))

prs.save("presentation.pptx")
```

### 常用操作

```python
# 设置字体
from pptx.util import Pt
run = paragraph.add_run()
run.text = "文本"
run.font.size = Pt(24)
run.font.bold = True

# 添加表格
rows, cols = 3, 4
table = slide.shapes.add_table(rows, cols, Inches(1), Inches(2), Inches(8), Inches(3)).table
table.cell(0, 0).text = "Header"

# 设置幻灯片尺寸（16:9）
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
```

### 与 Pencil MCP 配合

如果安装了 Pencil MCP，也可以用 Pencil 设计幻灯片布局，然后导出。适合需要精细视觉设计的场景。

---

## 跨技能工作流示例

### 示例 A：完整论文调研 → 文档撰写

```bash
# 1. 搜索论文
python3 skills/paper-research/scripts/arxiv_survey.py \
  --terms "egocentric action" --max-results 50 --out ./arxiv.jsonl

# 2. 生成报告
python3 skills/paper-research/scripts/generate_report.py \
  --jsonl ./arxiv.jsonl --out ./REPORT.md

# 3. 创建 Google Doc 并写入报告
REPORT=$(cat REPORT.md | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
echo "{\"title\": \"Literature Survey\", \"markdown\": $REPORT}" | \
  ~/.claude/skills/google-docs/scripts/docs_manager.rb create

# 4. 画架构图并插入文档
# （用 drawio 生成图，导出 PNG，上传 Drive，插入 Doc）
```

### 示例 B：Zotero 文献 → 对比表 → 演示文稿

```
1. 让 Claude 从 Zotero 搜索相关论文
2. 使用 paper_comparison_table.md 模板整理对比
3. 用 python-pptx 生成对比表演示文稿
4. 用 drawio 画方法对比图
```

---

## 安装指南

### 一键安装（推荐）

```bash
git clone git@github.com:LiYu0524/Auto-Reasearch-Skills.git ~/.claude/skills/auto-research
```

### 依赖安装

```bash
# Paper Research（Python，无额外依赖）
# 已内置，无需安装

# Zotero MCP
pip install zotero-mcp
claude mcp add-json "zotero" '{"command":"zotero-mcp","env":{"ZOTERO_LOCAL":"true"}}'

# Google Docs（Ruby gems）
/opt/homebrew/opt/ruby/bin/gem install google-apis-docs_v1 google-apis-drive_v3 googleauth

# Draw.io CLI
brew install --cask drawio

# PPTX
pip install python-pptx
```

### Google Docs 凭证配置

1. 在 [Google Cloud Console](https://console.cloud.google.com/) 创建项目
2. 启用 Google Docs API + Google Drive API
3. 创建 OAuth 2.0 桌面应用凭证
4. 下载 JSON 保存为 `~/.claude/.google/client_secret.json`
5. 运行 `~/.claude/skills/google-docs/scripts/docs_manager.rb help` 触发授权

---

## 文件结构

```
Auto-Research-Skills/
├── SKILL.md                          # 本文件（主入口）
├── README.md                         # GitHub 项目说明
├── skills/
│   ├── paper-research/               # 论文检索子技能
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── assets/
│   │   └── references/
│   ├── google-docs/                  # Google Docs 子技能
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── references/
│   ├── paper-banana/                 # 学术插图生成子技能
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── generate_figure.py
│   ├── drawio/                       # 架构图子技能
│   │   └── SKILL.md
│   ├── zotero/                       # Zotero 子技能
│   │   └── README.md
│   └── pptx/                         # 演示文稿子技能
│       └── README.md
└── assets/                           # 共享模板
    └── workflow_templates.md
```
