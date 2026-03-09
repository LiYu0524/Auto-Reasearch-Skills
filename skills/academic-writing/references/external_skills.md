# 外部推荐 Skills

来源：[awesome-ai-research-writing](https://github.com/Leey21/awesome-ai-research-writing) Part II

以下 Skills 可通过 OpenSkills 安装到 Cursor / Claude Code 中使用。

## Skills 总览

| Skill 名称 | 来源 | 功能简述 |
|------------|------|----------|
| **20-ml-paper-writing** | [zechenzhangAGI/AI-research-SKILLs](https://github.com/zechenzhangAGI/AI-research-SKILLs) | 面向 NeurIPS / ICML / ICLR / ACL / AAAI / COLM 的完整论文写作：从 repo 起稿、LaTeX 模板、引用验证、审稿人视角、会议 checklist、格式迁移；内含 booktabs 表格规范与图规范。 |
| **humanizer** | [blader/humanizer](https://github.com/blader/humanizer) | 识别并去除 AI 写作痕迹，使文本更自然。基于 Wikipedia「Signs of AI writing」。 |
| **docx** | [anthropics/skills](https://github.com/anthropics/skills) | 对 .docx 进行创建、编辑、分析。支持 Word 投稿模板填充和 Redlining 审稿修订。 |
| **doc-coauthoring** | [anthropics/skills](https://github.com/anthropics/skills) | 分阶段文档协作：收集上下文→按节头脑风暴→起草→精修→读者测试。 |
| **canvas-design** | [anthropics/skills](https://github.com/anthropics/skills) | 先产出 design philosophy (.md)，再在画布上实现为单页 .png / .pdf，适合论文概念图、框架图。 |

## 安装方式

```bash
# 安装 20-ml-paper-writing
npx openskills install zechenzhangAGI/AI-research-SKILLs

# 安装 Anthropic 官方 skills (docx, doc-coauthoring, canvas-design)
npx openskills install anthropics/skills
```

## 使用场景速查

| 使用场景 | 推荐 Skill | 示例 Prompt |
|----------|------------|-------------|
| 从零写论文 | 20-ml-paper-writing | 「用这个 repo 帮我写一篇投 NeurIPS 的论文」 |
| 用会议模板开新稿 | 20-ml-paper-writing | 「帮我用 ICLR 2026 模板新建一篇论文」 |
| 加引用 / 写 Related Work | 20-ml-paper-writing | 「帮我找并引用 2023 年后 RLHF 的几篇代表作」 |
| 换会议 / 改投 | 20-ml-paper-writing | 「这篇从 NeurIPS 改成 ICML 格式」 |
| 投稿前清单核对 | 20-ml-paper-writing | 「帮我对一下 NeurIPS 的 paper checklist」 |
| 写 LaTeX 表格 | 20-ml-paper-writing | 「用 booktabs 风格做一个对比表」 |
| 结构化写某一节 | doc-coauthoring | 「用协作流程写 Introduction」 |
| 论文概念图/框架图 | canvas-design | 「画一个方法的整体框架图」 |
| 去 AI 味终稿检查 | humanizer | 「投稿前帮我把 Abstract 去一下 AI 味」 |
| 用 Word 模板写稿 | docx | 「这是某期刊的 Word 模板，帮我填内容」 |
| 对 Word 稿做修订 | docx | 「按 redlining 流程标出需要改的几处」 |
