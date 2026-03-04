# PPTX 演示文稿生成

使用 [python-pptx](https://python-pptx.readthedocs.io/) 程序化生成 PowerPoint 演示文稿。

## 安装

```bash
pip install python-pptx
```

## 快速开始

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
# 设置 16:9 宽屏
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 标题页
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "研究报告"
slide.placeholders[1].text = "Author Name — 2026"

prs.save("output.pptx")
```

## 常用布局索引

| 索引 | 布局名称 | 用途 |
|------|---------|------|
| 0 | Title Slide | 标题页 |
| 1 | Title and Content | 标题+内容（最常用） |
| 2 | Section Header | 章节分隔页 |
| 5 | Blank | 空白页（自由布局） |
| 6 | Content with Caption | 带说明的内容 |

## 常用操作

### 添加文本框

```python
from pptx.util import Inches, Pt

txBox = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1))
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "自定义文本"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
```

### 添加图片

```python
slide.shapes.add_picture("figure.png", Inches(1), Inches(2), width=Inches(6))
```

### 添加表格

```python
rows, cols = 4, 3
table_shape = slide.shapes.add_table(rows, cols, Inches(1), Inches(2), Inches(8), Inches(3))
table = table_shape.table

# 设置表头
for i, header in enumerate(["方法", "Accuracy", "F1"]):
    table.cell(0, i).text = header

# 填充数据
table.cell(1, 0).text = "Baseline"
table.cell(1, 1).text = "0.85"
table.cell(1, 2).text = "0.82"
```

### 设置背景色

```python
from pptx.dml.color import RGBColor

background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0xF5, 0xF5, 0xF5)
```

### 添加形状

```python
from pptx.enum.shapes import MSO_SHAPE

shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(1), Inches(1), Inches(3), Inches(2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x40, 0x7B, 0xFF)
shape.text = "模块名称"
```

## 学术演示文稿模板

### 典型结构

```
1. Title Slide（标题页）
2. Outline（大纲）
3. Motivation / Problem（动机/问题）
4. Related Work（相关工作）
5. Method Overview（方法概述 — 配架构图）
6. Method Details（方法细节 × N 页）
7. Experiments Setup（实验设置）
8. Results（实验结果 — 表格/图表）
9. Ablation Study（消融实验）
10. Qualitative Results（定性结果 — 可视化）
11. Conclusion（结论）
12. Thank You / Q&A
```

## 与 draw.io 配合

1. 用 drawio 生成架构图并导出 PNG
2. 用 python-pptx 将 PNG 插入幻灯片

```python
# 架构图占满幻灯片（留边距）
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title  # 如果有标题
slide.shapes.add_picture(
    "architecture.drawio.png",
    Inches(0.5), Inches(1.5),
    width=Inches(12.3)
)
```

## 与 Pencil MCP 配合

Pencil MCP 适合需要精细视觉设计的场景：
1. 在 Pencil 中设计幻灯片布局
2. 导出为图片
3. 用 python-pptx 组装成最终 .pptx
