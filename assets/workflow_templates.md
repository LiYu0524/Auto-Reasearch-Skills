# 工作流模板

## 模板 A：完整论文调研

```
目标：对某个研究方向进行系统性文献调研

步骤：
1. [paper-research] 用 arxiv_survey.py 搜索 100-200 篇论文
2. [paper-research] 用 generate_report.py 生成结构化报告
3. [zotero] 将关键论文导入 Zotero 并分类标签
4. [zotero] 提取已读论文的 PDF 注释
5. [google-docs] 创建 Google Doc 文献综述
6. [google-docs] 逐步填充各章节内容
7. [drawio] 画研究领域 taxonomy 图
8. [google-docs] 将图片插入文档

产出：文献综述 Google Doc + refs.bib + taxonomy 图
```

## 模板 B：论文写作支持

```
目标：支撑一篇论文的写作过程

步骤：
1. [google-docs] 创建论文草稿 Google Doc
2. [drawio] 画方法架构图
3. [pptx] 制作实验结果对比表的可视化
4. [paper-research] 补充 Related Work 的引用
5. [zotero] 导出最终 BibTeX
6. [google-docs] 最终版本校对和格式调整

产出：论文草稿 + 架构图 + 实验可视化 + BibTeX
```

## 模板 C：会议演示准备

```
目标：为论文准备会议 oral/poster 演示

步骤：
1. [google-docs] 读取论文终稿内容
2. [drawio] 重新绘制简化版架构图（适合演示）
3. [pptx] 生成演示文稿框架（标题+大纲+各章节）
4. [pptx] 插入架构图、实验结果图表
5. [pptx] 调整排版和配色

产出：.pptx 演示文稿
```

## 模板 D：周会/组会汇报

```
目标：准备每周研究进展汇报

步骤：
1. [zotero] 列出本周新读的论文及注释
2. [drawio] 画本周实验流程/结果对比图
3. [pptx] 生成简短汇报文稿（5-10 页）
4. [google-docs] 更新进展日志文档

产出：周报 .pptx + 进展日志更新
```
