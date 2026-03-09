---
name: academic-writing
description: |
  学术论文写作 Prompt 工具箱：中英翻译、润色、缩写/扩写、逻辑检查、去 AI 味、
  实验分析、图表标题生成、架构图描述、实验绘图推荐、Reviewer 视角审稿。
  来源：awesome-ai-research-writing（MSRA / Seed / SH AI Lab 等顶尖研究机构实战 Prompt）。
version: 1.0.0
---

# Academic Writing（学术论文写作 Prompt 工具箱）

来源：[awesome-ai-research-writing](https://github.com/Leey21/awesome-ai-research-writing)
由 MSRA、Seed、SH AI Lab 等顶尖研究机构的研究员，以及北大、中科大、上交的硕博同学实战打磨。

## 使用方式

当用户提出以下写作需求时，从 `references/writing_prompts.md` 中加载对应的 Prompt 模板，
将用户提供的文本填入 `[Input]` 部分后执行：

| 场景 | Prompt 名称 | 说明 |
|------|-------------|------|
| 中文草稿 → 英文论文 | 中转英 | LaTeX 格式输出 + 中文直译核对 |
| 英文论文 → 中文理解 | 英转中 | 去 LaTeX 命令，纯中文输出 |
| 中文草稿 → 中文论文 | 中转中 | 适配 Word，逻辑重组 |
| 压缩文本长度 | 缩写 | 减少 5-15 词，保留所有信息 |
| 扩充文本内容 | 扩写 | 增加 5-15 词，挖掘隐含逻辑 |
| 英文论文润色 | 表达润色（英文） | 深度润色，零错误标准 |
| 中文论文润色 | 表达润色（中文） | 尊重原著，克制修改 |
| 逻辑与一致性审查 | 逻辑检查 | 仅报致命错误 |
| 去除英文 AI 痕迹 | 去 AI 味（LaTeX 英文） | 词汇 + 结构自然化 |
| 去除中文 AI 痕迹 | 去 AI 味（Word 中文） | 去翻译腔与机械感 |
| 论文架构图描述 | 论文架构图 | 生成架构图的详细描述/指令 |
| 选择实验图表类型 | 实验绘图推荐 | 从 19 种学术图表中推荐 |
| 生成 Figure caption | 生成图的标题 | Title Case / Sentence case |
| 生成 Table caption | 生成表的标题 | 学术标准表达 |
| 实验结果分析 | 实验分析 | LaTeX \paragraph 结构输出 |
| 模拟审稿 | Reviewer 审视 | 严苛模式 + 改稿建议 |

## 触发条件

当用户请求涉及以下关键词时自动触发：
- 翻译、润色、缩写、扩写、改写
- 去 AI 味、humanize、去机器味
- 逻辑检查、审稿、review
- 图标题、表标题、caption
- 实验分析、绘图推荐
- 架构图

## AI 高频词黑名单

参见 `references/ai_words_blacklist.md`，在润色和去 AI 味时参考。

## 外部推荐 Skills

参见 `references/external_skills.md`，包含 20-ml-paper-writing、humanizer、docx 等外部技能的介绍与使用场景。
